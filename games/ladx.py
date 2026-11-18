"""Link's Awakening DX (Game Boy Color), and the original Game Boy release.

Save layout from zladx/LADX-Disassembly (src/constants/memory/sram.asm): the SRAM
skips $100 bytes, then holds three slots. Each slot is a 5-byte "1 3 5 7 9" prefix,
a $380-byte copy of WRAM $D800-$DB7F, then (DX only) $28 more bytes for the Color
Dungeon, the tunic and the photo album.

Which room flag marks which check: LADXR's check table and the Magpie/Archipelago
autotracker (room status byte at $D800 + room, bit $10 for items, $20 for boss
Heart Containers).
"""

from __future__ import annotations

from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef, bcd, popcount

PREFIX = bytes([1, 3, 5, 7, 9])
SLOT_BASE = 0x100
MAIN_SIZE = 0x380
STRIDE_DX = 5 + MAIN_SIZE + 5 + 0x20 + 3     # $3AD
STRIDE_GB = 5 + MAIN_SIZE                     # $385

INVENTORY = 0xDB00          # 12 slots of item ids
NAME = 0xDB4F               # 5 bytes, ASCII + 1
MAX_HEARTS = 0xDB5B
HEART_PIECES = 0xDB5C
SEASHELLS = 0xDB0F          # BCD

# (room, name, area, hint)
HEART_PIECES_LIST = [
    (0x2A4, "Mabe Village well", "Mabe Village", "Drop down the well in Mabe Village."),
    (0x2B1, "Fishing pond", "Mabe Village", "Catch the big fish at the fishing pond."),
    (0x044, "Heart Piece of Shame", "Koholint Prairie",
     "Freestanding on the prairie, on a spot that's hard to reach at first."),
    (0x2DF, "Graveyard connector cave", "Koholint Prairie",
     "In the cave under the Graveyard (Bombs, Roc's Feather, and the Hookshot or Pegasus Boots)."),
    (0x2AB, "Skull cave", "Mysterious Woods", "In a cave in the Mysterious Woods."),
    (0x2E5, "Boots 'n' Bomb cave", "Ukuku Prairie",
     "Bomb your way into the cave, then dash with the Pegasus Boots."),
    (0x078, "Castle moat", "Kanalet Castle", "Dive in Kanalet Castle's moat with the Flippers."),
    (0x2E6, "Bomb arrow cave", "Yarna Desert", "In a cave near Animal Village (Bombs, Roc's Feather and the Hookshot)."),
    (0x1E8, "Cave under the Lanmola", "Yarna Desert",
     "Beat the Lanmola, then drop into its quicksand pit."),
    (0x1F2, "Damp cave", "Tal Tal Heights", "In the damp cave on Tal Tal Heights."),
    (0x2BA, "Access tunnel", "Tal Tal Mountains", "Bomb the wall in the mountain access tunnel."),
    (0x000, "Outside Turtle Rock", "Tal Tal Mountains", "Near the entrance to Turtle Rock."),
]

BOSSES = [
    (0x106, "Moldorm", "Tail Cave"), (0x12B, "Genie", "Bottle Grotto"),
    (0x15A, "Slime Eye", "Key Cavern"), (0x166, "Angler Fish", "Angler's Tunnel"),
    (0x185, "Slime Eel", "Catfish's Maw"), (0x1BC, "Facade", "Face Shrine"),
    (0x223, "Evil Eagle", "Eagle's Tower"), (0x234, "Hot Head", "Turtle Rock"),
]

INSTRUMENTS = [
    "Full Moon Cello", "Conch Horn", "Sea Lily's Bell", "Surf Harp",
    "Wind Marimba", "Coral Triangle", "Organ of Evening Calm", "Thunder Drum",
]

# Hidden seashells (bushes, digging, trees, rocks). The rest come from chests and gifts.
SEASHELL_SPOTS = [
    (0x0A3, "Bush field", "Mabe Village"), (0x2B2, "Dig by the dog house", "Mabe Village"),
    (0x0D2, "Tree outside Tail Cave (dash into it)", "Toronbo Shores"),
    (0x074, "Dig by the ghost's grave", "Koholint Prairie"),
    (0x0A5, "Dig on the ledge outside Key Cavern", "Ukuku Prairie"),
    (0x0A6, "Bush on the island outside Key Cavern", "Ukuku Prairie"),
    (0x08B, "Bush east of the Seashell Mansion", "Ukuku Prairie"),
    (0x0A4, "Tree east of Mabe Village (dash into it)", "Ukuku Prairie"),
    (0x0B9, "Under a rock", "Donut Plains"), (0x0A8, "Dig on the ledge", "Donut Plains"),
    (0x0E9, "Lone bush", "Martha's Bay"), (0x0F8, "Bush on the island", "Martha's Bay"),
    (0x0DA, "Dig on the peninsula", "Martha's Bay"), (0x1E3, "Barrel in the ghost's house", "Martha's Bay"),
    (0x0FF, "Under a rock", "Yarna Desert"), (0x00C, "Rock by the bridge", "Tal Tal Mountains"),
]

ITEMS = [  # (inventory id, name, hint)
    (0x02, "Bombs", "Buy them at the Mabe Village shop."),
    (0x05, "Bow", "Mabe Village shop (980 Rupees)."),
    (0x06, "Hookshot", "Catfish's Maw (Level 5)."),
    (0x07, "Magic Rod", "Turtle Rock (Level 8)."),
    (0x08, "Pegasus Boots", "Key Cavern (Level 3)."),
    (0x09, "Ocarina", "From the dream shrine in Mabe Village."),
    (0x0A, "Roc's Feather", "Tail Cave (Level 1)."),
    (0x0B, "Shovel", "Mabe Village shop."),
    (0x0C, "Magic Powder", "Bring the Toadstool to the Witch."),
    (0x0D, "Boomerang", "Trade for it in the cave on Toronbo Shores."),
]


def _decode_name(raw: bytes) -> str:
    return "".join(" " if b == 0 else chr(b - 1) if 0x21 < b < 0x80 else "?" for b in raw).strip()


class _Slot:
    def __init__(self, data: bytes, base: int, dx: bool):
        self.main = data[base + 5:base + 5 + MAIN_SIZE]
        self.dx = dx
        ext = data[base + 5 + MAIN_SIZE:base + STRIDE_DX] if dx else b""
        self.dx1, self.dx2, self.dx3 = ext[:5], ext[5:0x25], ext[0x25:0x28]

    def ram(self, addr: int) -> int:
        if 0xD800 <= addr < 0xDB80:
            return self.main[addr - 0xD800]
        if self.dx and 0xDDE0 <= addr < 0xDE00:
            return self.dx2[addr - 0xDDE0]
        if self.dx and 0xDDDA <= addr < 0xDDDF:
            return self.dx1[addr - 0xDDDA]
        return 0

    def room(self, room: int, mask: int = 0x10) -> bool:
        addr = 0xDDE0 + (room - 0x300) if room >= 0x300 else 0xD800 + room
        return bool(self.ram(addr) & mask)

    def has_item(self, item: int) -> bool:
        return item in self.main[0x300:0x30C]


def _layout(data: bytes) -> tuple[bool, list[int]]:
    """(is_dx, valid slot bases)."""
    def valid(stride):
        return [SLOT_BASE + i * stride for i in range(3)
                if data[SLOT_BASE + i * stride:SLOT_BASE + i * stride + 5] == PREFIX]
    dx, gb = valid(STRIDE_DX), valid(STRIDE_GB)
    # slot 1 always lines up; the others tell DX and GB apart
    if len(gb) > len(dx):
        return False, gb
    return True, dx


class LinksAwakening(Game):
    id, title, short, platform = "ladx", "Link's Awakening DX", "LADX", "Game Boy Color"
    file_help = "the .sav (or .srm) file your Game Boy emulator writes next to the ROM"

    def detect(self, path: Path, data: bytes) -> bool:
        return len(data) in (0x2000, 0x8000) and bool(_layout(data)[1])

    def slots(self, path: Path) -> list[SlotRef]:
        dx, bases = _layout(path.read_bytes())
        stride = STRIDE_DX if dx else STRIDE_GB
        return [SlotRef(path, (b - SLOT_BASE) // stride) for b in bases]

    def read(self, slot: SlotRef) -> Result:
        data = slot.path.read_bytes()
        dx, bases = _layout(data)
        stride = STRIDE_DX if dx else STRIDE_GB
        base = SLOT_BASE + (slot.index or 0) * stride
        if base not in bases:
            raise SaveError(f"Slot {(slot.index or 0) + 1} in {slot.path.name} is empty.")
        s = _Slot(data, base, dx)
        y = lambda ok: "yes" if ok else None  # noqa: E731

        name = _decode_name(s.main[NAME - 0xD800:NAME - 0xD800 + 5]) or "(no name)"
        hearts = s.ram(MAX_HEARTS)
        in_progress = s.ram(HEART_PIECES) & 3
        bosses = [b for b in BOSSES if s.room(b[0], 0x20)]

        res = Result(self, slot, name, hearts, in_progress)
        if not dx:
            res.tags.append("Game Boy")

        hp = Section("hearts", "Pieces of Heart", None, [
            Row(f"hp_{room:03x}", n, hint, y(s.room(room)), group=area)
            for room, n, area, hint in HEART_PIECES_LIST
        ])
        expected = max(0, (hearts - 3 - len(bosses)) * 4 + in_progress)
        hp.intro = f"{hp.done} of {len(hp.rows)} pieces · {len(bosses)} of 8 boss Heart Containers."
        if expected > hp.done:
            hp.banner = (f"Your hearts show {expected - hp.done} more piece(s) than the save's flags "
                         "account for. One of the pieces marked missing may already be yours.")

        shells = bcd(s.ram(SEASHELLS))
        shell_sec = Section("seashells", "Secret Seashells", "weather-clear-night-symbolic", [
            Row(f"sh_{room:03x}", n, "Hidden: dig, cut, lift or dash into it.", y(s.room(room)), group=area)
            for room, n, area in SEASHELL_SPOTS
        ])
        shell_sec.intro = (f"You've collected {shells} seashells in all. These are the hidden ones; "
                           "the rest come from chests, shops and gifts. 20 earn the L-2 Sword.")

        res.sections = [
            hp,
            Section("bosses", "Heart Containers", "emblem-favorite-symbolic", [
                Row(f"hc_{room:03x}", f"{boss} Heart Container", where, y(s.room(room, 0x20)))
                for room, boss, where in BOSSES
            ]),
            Section("instruments", "Instruments of the Sirens", "audio-x-generic-symbolic", [
                Row(f"in_{i + 1}", n, f"Level {i + 1} dungeon.", y(s.ram(0xDB65 + i) & 0x02))
                for i, n in enumerate(INSTRUMENTS)
            ]),
            Section("songs", "Songs", "media-playback-start-symbolic", [
                Row("so_ballad", "Ballad of the Wind Fish", "Marin teaches it in Mabe Village.",
                    y(s.ram(0xDB49) & 0x04)),
                Row("so_mambo", "Manbo's Mambo", "Manbo, in the pond on Tal Tal Heights.",
                    y(s.ram(0xDB49) & 0x02)),
                Row("so_frog", "Frog's Song of Soul", "Mamu, in the cave in Signpost Maze.",
                    y(s.ram(0xDB49) & 0x01)),
            ]),
            Section("items", "Items", "view-grid-symbolic", [
                Row("it_sword", "Sword", "Washed up on Toronbo Shores.", y(s.ram(0xDB4E) >= 1)),
                Row("it_shield", "Shield", "From Tarin at the start.", y(s.ram(0xDB44) >= 1)),
                Row("it_bracelet", "Power Bracelet", "Bottle Grotto (Level 2).", y(s.ram(0xDB43) >= 1)),
                *[Row(f"it_{i:02x}", n, h, y(s.has_item(i))) for i, n, h in ITEMS],
                Row("it_flippers", "Flippers", "Angler's Tunnel (Level 4).", y(s.ram(0xDB0C))),
            ]),
            Section("upgrades", "Upgrades", "go-up-symbolic", [
                Row("up_sword2", "L-2 Sword", "Bring 20 seashells to the Seashell Mansion.",
                    y(s.ram(0xDB4E) >= 2)),
                Row("up_shield2", "Mirror Shield", "Eagle's Tower (Level 7).",
                    y(s.ram(0xDB44) >= 2)),
                Row("up_bracelet2", "L-2 Power Bracelet", "Face Shrine (Level 6).", y(s.ram(0xDB43) >= 2)),
                Row("up_powder", "More Magic Powder", "One of the three Mad Batters.", y(s.ram(0xDB76) > 0x20)),
                Row("up_bombs", "More Bombs", "One of the three Mad Batters.", y(s.ram(0xDB77) > 0x30)),
                Row("up_arrows", "More Arrows", "One of the three Mad Batters.", y(s.ram(0xDB78) > 0x30)),
            ]),
            Section("quest", "Quest", "starred-symbolic", [
                Row("qu_leaves", "Five Golden Leaves", "Found around Kanalet Castle.", y(s.ram(0xDB15) >= 5),
                    f"{min(s.ram(0xDB15), 5)} of 5 leaves"),
                Row("qu_trade", "Trading sequence", "Trade all the way to the Magnifying Lens.",
                    y(s.ram(0xDB0E) >= 0x0E)),
                *([Row("qu_tunic", "Color Dungeon tunic", "Finish the Color Dungeon (DX only).",
                       y(s.dx3[0] in (1, 2)))] if dx else []),
            ]),
            shell_sec,
        ]
        if dx:
            photos = popcount(s.dx3[1]) + popcount(s.dx3[2] & 0x0F)
            res.sections.append(Section("photos", "Photo Album", "camera-photo-symbolic", [
                Row(f"ph_{i + 1}", f"Photo {i + 1}", "Visit the Camera Shop's mouse around the island.",
                    y(i < photos)) for i in range(12)
            ], intro=f"{photos} of 12 photos. The save only stores which photos you have, "
                     "so they're counted rather than named."))
        res.footnote = ("Not tracked: owl statues, small keys and dungeon maps. The seashell list "
                        "covers the hidden ones; your total seashell count is shown on that page.")
        return res
