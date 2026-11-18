"""A Link to the Past (Super Nintendo; the .srm/.sav your SNES emulator writes).

SRAM layout (well documented by the ALttP randomizer community): three $500-byte
files at $0000/$0500/$0A00, each a copy of WRAM $7EF000. Room flags are 16-bit
words at room*2, overworld screens are bytes at $280+screen (bit $40 = item taken).
Which flag belongs to which location comes from Archipelago's ALttP client.

Only the SNES version is supported; the GBA release stores its save differently.
"""

from __future__ import annotations

import struct
from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef, popcount

SLOT_SIZE = 0x500

# (key, name, area, kind, a, b) — kind "ow": screen a; "uw": room a with mask b
PIECES = [
    ("sunken", "Sunken Treasure", "Light World", "ow", 0x3B, 0),
    ("zora", "Zora's Ledge", "Light World", "ow", 0x81, 0),
    ("lake_island", "Lake Hylia Island", "Light World", "ow", 0x35, 0),
    ("maze_race", "Maze Race", "Light World", "ow", 0x28, 0),
    ("desert_ledge", "Desert Ledge", "Light World", "ow", 0x30, 0),
    ("spectacle", "Spectacle Rock", "Death Mountain", "ow", 0x03, 0),
    ("floating", "Floating Island", "Death Mountain", "ow", 0x05, 0),
    ("kak_well", "Kakariko Well", "Light World", "uw", 0x2F, 0x10),
    ("lumberjack", "Lumberjack Tree", "Light World", "uw", 0xE2, 0x200),
    ("cave45", "Cave 45", "Light World", "uw", 0x11B, 0x400),
    ("graveyard", "Graveyard Ledge cave", "Light World", "uw", 0x11B, 0x200),
    ("checkerboard", "Checkerboard Cave", "Light World", "uw", 0x126, 0x200),
    ("spectacle_cave", "Spectacle Rock Cave", "Death Mountain", "uw", 0xEA, 0x400),
    ("mimic", "Mimic Cave", "Death Mountain", "uw", 0x10C, 0x10),
    ("pyramid", "Pyramid ledge", "Dark World", "ow", 0x5B, 0),
    ("bumper", "Bumper Cave Ledge", "Dark World", "ow", 0x4A, 0),
    ("digging", "Digging Game", "Dark World", "ow", 0x68, 0),
    ("chest_game", "Treasure Chest Game", "Dark World", "uw", 0x106, 0x400),
    ("peg_cave", "Peg Cave", "Dark World", "uw", 0x127, 0x400),
]
TOTAL_PIECES = 24

BOSSES = [  # (room, mask, name)
    (0x12, 0x10, "Sanctuary"), (0xC8, 0x800, "Eastern Palace"), (0x33, 0x800, "Desert Palace"),
    (0x07, 0x800, "Tower of Hera"), (0x5A, 0x800, "Palace of Darkness"), (0x06, 0x800, "Swamp Palace"),
    (0x29, 0x800, "Skull Woods"), (0xAC, 0x800, "Thieves' Town"), (0xDE, 0x800, "Ice Palace"),
    (0x90, 0x800, "Misery Mire"), (0xA4, 0x800, "Turtle Rock"),
]

CRYSTALS = [  # (bit mask in $37A, dungeon)
    (0x02, "Palace of Darkness"), (0x10, "Swamp Palace"), (0x40, "Skull Woods"),
    (0x20, "Thieves' Town"), (0x04, "Ice Palace"), (0x01, "Misery Mire"), (0x08, "Turtle Rock"),
]


def _valid(blob: bytes) -> bool:
    return len(blob) >= SLOT_SIZE and blob[0x3E5:0x3E7] in (b"\x55\xAA", b"\xAA\x55")


class _View:
    def __init__(self, blob: bytes):
        self.b = blob

    def u8(self, off: int) -> int:
        return self.b[off]

    def uw(self, room: int, mask: int) -> bool:
        return bool(struct.unpack_from("<H", self.b, room * 2)[0] & mask)

    def ow(self, screen: int) -> bool:
        return bool(self.b[0x280 + screen] & 0x40)


class LinkToThePast(Game):
    id, title, short, platform = "alttp", "A Link to the Past", "ALttP", "Super Nintendo"
    file_help = "the .srm (or .sav) file your SNES emulator writes next to the ROM"

    def detect(self, path: Path, data: bytes) -> bool:
        return len(data) in (0x2000, 0x8000) and any(_valid(data[i * SLOT_SIZE:]) for i in range(3))

    def slots(self, path: Path) -> list[SlotRef]:
        data = path.read_bytes()
        return [SlotRef(path, i) for i in range(3) if _valid(data[i * SLOT_SIZE:])]

    def read(self, slot: SlotRef) -> Result:
        data = slot.path.read_bytes()
        blob = data[(slot.index or 0) * SLOT_SIZE:(slot.index or 0) * SLOT_SIZE + SLOT_SIZE]
        if not _valid(blob):
            raise SaveError(f"File {(slot.index or 0) + 1} in {slot.path.name} is empty.")
        v = _View(blob)
        y = lambda ok: "yes" if ok else None  # noqa: E731

        hearts, in_progress = v.u8(0x36C) // 8, v.u8(0x36B) & 3
        res = Result(self, slot, f"File {(slot.index or 0) + 1}", hearts, in_progress)

        boss_rows = [Row(f"hc_{room:x}", f"{name} Heart Container",
                         "In the Sanctuary's chest." if name == "Sanctuary" else "Beat the boss.",
                         y(v.uw(room, mask))) for room, mask, name in BOSSES]
        containers = sum(r.ok for r in boss_rows)
        known = [Row(f"hp_{k}", n, "", y(v.ow(a) if kind == "ow" else v.uw(a, b)), group=area)
                 for k, n, area, kind, a, b in PIECES]
        total = min(TOTAL_PIECES, max(0, (hearts - 3 - containers) * 4 + in_progress))
        spare = max(0, total - sum(r.ok for r in known))
        others = [Row(f"hp_other{i + 1}", f"Other Piece of Heart {i + 1}",
                      "Counted from your hearts; this tracker doesn't have its flag yet.",
                      "inferred" if i < spare else None, group="Counted from your hearts")
                  for i in range(TOTAL_PIECES - len(known))]
        hp = Section("hearts", "Pieces of Heart", None, known + others,
                     intro=f"Your hearts show {total} of 24 pieces.")

        bow, boom, flute = v.u8(0x340), v.u8(0x341), v.u8(0x34C)
        sword, shield, armor = v.u8(0x359), v.u8(0x35A), v.u8(0x35B)
        gloves, magic = v.u8(0x354), v.u8(0x37B)
        bottles = sum(1 for i in range(4) if v.u8(0x35C + i))
        items = [
            ("bow", "Bow", bow >= 1), ("boomerang", "Boomerang", boom >= 1),
            ("hookshot", "Hookshot", v.u8(0x342)), ("bombs", "Bombs", v.u8(0x343) or v.u8(0x370)),
            ("mushroom", "Mushroom / Magic Powder", v.u8(0x344)), ("fire_rod", "Fire Rod", v.u8(0x345)),
            ("ice_rod", "Ice Rod", v.u8(0x346)), ("bombos", "Bombos Medallion", v.u8(0x347)),
            ("ether", "Ether Medallion", v.u8(0x348)), ("quake", "Quake Medallion", v.u8(0x349)),
            ("lamp", "Lamp", v.u8(0x34A)), ("hammer", "Magic Hammer", v.u8(0x34B)),
            ("shovel", "Shovel", flute >= 1), ("flute", "Flute", flute >= 2),
            ("net", "Bug-Catching Net", v.u8(0x34D)), ("book", "Book of Mudora", v.u8(0x34E)),
            ("somaria", "Cane of Somaria", v.u8(0x350)), ("byrna", "Cane of Byrna", v.u8(0x351)),
            ("cape", "Magic Cape", v.u8(0x352)), ("mirror", "Magic Mirror", v.u8(0x353) >= 2),
            ("boots", "Pegasus Boots", v.u8(0x355)), ("flippers", "Zora's Flippers", v.u8(0x356)),
            ("pearl", "Moon Pearl", v.u8(0x357)), ("glove", "Power Glove", gloves >= 1),
        ]
        res.sections = [
            hp,
            Section("bosses", "Heart Containers", "emblem-favorite-symbolic", boss_rows),
            Section("pendants", "Pendants", "starred-symbolic", [
                Row("pe_courage", "Pendant of Courage", "Eastern Palace.", y(v.u8(0x374) & 0x04)),
                Row("pe_power", "Pendant of Power", "Desert Palace.", y(v.u8(0x374) & 0x02)),
                Row("pe_wisdom", "Pendant of Wisdom", "Tower of Hera.", y(v.u8(0x374) & 0x01)),
            ]),
            Section("crystals", "Crystals", "weather-clear-night-symbolic", [
                Row(f"cr_{i + 1}", f"Crystal {i + 1}", f"{d}.", y(v.u8(0x37A) & m))
                for i, (m, d) in enumerate(CRYSTALS)
            ]),
            Section("items", "Items", "view-grid-symbolic",
                    [Row(f"it_{k}", n, "", y(ok)) for k, n, ok in items]),
            Section("upgrades", "Upgrades", "go-up-symbolic", [
                Row("up_master", "Master Sword", "Lost Woods pedestal.", y(sword >= 2)),
                Row("up_tempered", "Tempered Sword", "The Smithy, after rescuing his partner.", y(sword >= 3)),
                Row("up_golden", "Golden Sword", "Throw the Tempered Sword into the Pyramid fairy's pond.", y(sword >= 4)),
                Row("up_red_boomerang", "Magical Boomerang", "The Waterfall of Wishing fairy.", y(boom >= 2)),
                Row("up_silver", "Silver Arrows", "The Pyramid fairy.", y(bow >= 3)),
                Row("up_titans", "Titan's Mitt", "Thieves' Town.", y(gloves >= 2)),
                Row("up_fire_shield", "Red Shield", "The Waterfall of Wishing fairy.", y(shield >= 2)),
                Row("up_mirror_shield", "Mirror Shield", "Turtle Rock.", y(shield >= 3)),
                Row("up_blue_mail", "Blue Mail", "Ice Palace.", y(armor >= 1)),
                Row("up_red_mail", "Red Mail", "Ganon's Tower.", y(armor >= 2)),
                Row("up_half_magic", "Half Magic", "The Magic Bat.", y(magic >= 1)),
                Row("up_bombs", "More bombs", "Pond of Happiness fairy.", y(v.u8(0x370))),
                Row("up_arrows", "More arrows", "Pond of Happiness fairy.", y(v.u8(0x371))),
            ]),
            Section("bottles", "Bottles", "applications-science-symbolic",
                    [Row(f"bt_{k + 1}", f"Bottle {k + 1}", "", y(k < bottles)) for k in range(4)]),
        ]
        res.footnote = ("Not tracked: small keys, maps and the chests that only hold rupees. Five Pieces "
                        "of Heart are counted from your hearts until their flags are confirmed.")
        return res
