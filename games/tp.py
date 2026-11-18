"""Twilight Princess (GameCube): the .gci file Dolphin or a GameCube save manager exports.

Save layout from zeldaret/tp (include/d/d_save.h, include/m_Do/m_Do_MemCard.h,
src/m_Do/m_Do_MemCardRWmng.cpp): the 0x8000-byte card file holds its game data at
0x4000 (backup at 0x6000): two words, then three 0xA94-byte quest logs. Big-endian.
A .gci adds a 0x40-byte header in front.

Only the GameCube release is supported; the Wii and HD versions store saves differently.
"""

from __future__ import annotations

import struct
from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef, popcount

GCI_HEADER = 0x40
DATA = 0x4000
BACKUP = 0x6000
LOG_SIZE = 0xA94

# offsets inside a quest log (dSv_save_c -> dSv_player_c)
MAX_LIFE = 0x000          # u16, 5 per heart
WALLET = 0x019
ITEMS = 0x09C             # u8[24] item ids
GET_ITEM = 0x0CC          # u32[8] "obtained once" flags by item id
COLLECT = 0x100           # u8[8] equipment bitfields
CRYSTAL = 0x109           # Fused Shadows
MIRROR = 0x10A            # Mirror Shards
POE_SOULS = 0x10C
LETTERS = 0x11C           # u32[2]
NAME = 0x1B4              # char[16]

BUGS = ["Beetle", "Butterfly", "Stag Beetle", "Grasshopper", "Phasmid", "Pill Bug",
        "Mantis", "Ladybug", "Snail", "Dragonfly", "Ant", "Dayfly"]

ITEM_LIST = [  # (item id, name, hint)
    (0x4B, "Slingshot", "Sera's shop in Ordon."),
    (0x48, "Lantern", "From Coro in Faron Woods."),
    (0x40, "Gale Boomerang", "Forest Temple."),
    (0x45, "Iron Boots", "From Bo in Ordon."),
    (0x43, "Hero's Bow", "Goron Mines."),
    (0x3E, "Hawkeye", "Kakariko Village shop."),
    (0x50, "Bomb Bag", "From Barnes in Kakariko."),
    (0x44, "Clawshot", "Lakebed Temple."),
    (0x41, "Spinner", "Arbiter's Grounds."),
    (0x42, "Ball and Chain", "Snowpeak Ruins."),
    (0x46, "Dominion Rod", "Temple of Time."),
    (0x47, "Double Clawshots", "City in the Sky."),
    (0x4A, "Fishing Rod", "From Uli in Ordon, after you return her cradle."),
    (0x84, "Horse Call", "From Ilia."),
]
GEAR = [
    (0x28, "Ordon Sword", ""), (0x29, "Master Sword", "Sacred Grove."),
    (0x49, "Light-filled Master Sword", "After the Palace of Twilight."),
    (0x2A, "Wooden Shield", ""), (0x2C, "Hylian Shield", ""),
    (0x31, "Zora Armor", "From Rutela."), (0x30, "Magic Armor", "Castle Town shop."),
    (0x35, "Big Wallet", "Agitha's reward."), (0x36, "Giant Wallet", "Agitha's reward."),
    (0x55, "Big Quiver", ""), (0x56, "Giant Quiver", ""),
]
BOTTLE_IDS = set(range(0x60, 0x80)) | {0x9C, 0x9D, 0x9E, 0x9F}


def _base(data: bytes) -> int:
    """Offset of the card file inside `data` (0x40 for a .gci, 0 for a bare file), or -1."""
    if data[:3] == b"GZ2" and len(data) >= GCI_HEADER + 0x8000:
        return GCI_HEADER
    if len(data) == 0x8000:
        return 0
    return -1


def _log_ok(log: bytes) -> bool:
    life = struct.unpack_from(">H", log, MAX_LIFE)[0]
    return 15 <= life <= 100 and any(log[NAME:NAME + 16])


def _logs(data: bytes) -> list[tuple[int, int]]:
    b = _base(data)
    if b < 0:
        return []
    out = []
    for i in range(3):
        for area in (DATA, BACKUP):
            off = b + area + 8 + i * LOG_SIZE
            if len(data) >= off + LOG_SIZE and _log_ok(data[off:off + LOG_SIZE]):
                out.append((i, off))
                break
    return out


class TwilightPrincess(Game):
    id, title, short, platform = "tp", "Twilight Princess", "TP", "GameCube"
    file_help = "the .gci file Dolphin exports (Memory Card Manager → Export)"

    def detect(self, path: Path, data: bytes) -> bool:
        return bool(_logs(data))

    def slots(self, path: Path) -> list[SlotRef]:
        return [SlotRef(path, i) for i, _o in _logs(path.read_bytes())]

    def read(self, slot: SlotRef) -> Result:
        data = slot.path.read_bytes()
        found = dict(_logs(data))
        if slot.index not in found:
            raise SaveError(f"Quest Log {(slot.index or 0) + 1} in {slot.path.name} is empty.")
        q = data[found[slot.index]:found[slot.index] + LOG_SIZE]
        y = lambda ok: "yes" if ok else None  # noqa: E731

        def got(item: int) -> bool:
            word = struct.unpack_from(">I", q, GET_ITEM + (item >> 5) * 4)[0]
            return bool(word >> (item & 31) & 1)

        name = q[NAME:NAME + 16].split(b"\0")[0].decode("latin-1", "replace").strip() or "(no name)"
        life = struct.unpack_from(">H", q, MAX_LIFE)[0]
        hearts, pieces = life // 5, life % 5
        res = Result(self, slot, name, hearts, pieces, pieces_per_heart=5)

        extra = hearts - 3
        heart_sec = Section("hearts", "Hearts", None, [
            Row(f"ht_{k + 4}", f"Heart {k + 4}", "", y(k < extra)) for k in range(17)
        ], intro=(f"{hearts} of 20 hearts, plus {pieces}/5 toward the next. 8 come from bosses and 9 from "
                  "the 45 Pieces of Heart; this tracker doesn't read which pieces you found yet."))

        poes = q[POE_SOULS]
        letters = popcount(struct.unpack_from(">Q", q, LETTERS)[0])
        bottles = sum(1 for b in q[ITEMS:ITEMS + 24] if b in BOTTLE_IDS)
        bug_rows = []
        for i, bug in enumerate(BUGS):
            for sex, off in (("Male", 0), ("Female", 1)):
                bug_rows.append(Row(f"bg_{i * 2 + off}", f"{sex} {bug}", "Give it to Agitha in Castle Town.",
                                    y(got(0xC0 + i * 2 + off)), group=bug))

        res.sections = [
            heart_sec,
            Section("quest", "Fused Shadows & Mirror Shards", "starred-symbolic", [
                Row("fs_1", "Fused Shadow 1", "Forest Temple.", y(q[CRYSTAL] & 1)),
                Row("fs_2", "Fused Shadow 2", "Goron Mines.", y(q[CRYSTAL] & 2)),
                Row("fs_3", "Fused Shadow 3", "Lakebed Temple.", y(q[CRYSTAL] & 4)),
                Row("ms_1", "Mirror Shard 1", "Arbiter's Grounds.", y(q[MIRROR] & 1)),
                Row("ms_2", "Mirror Shard 2", "Snowpeak Ruins.", y(q[MIRROR] & 2)),
                Row("ms_3", "Mirror Shard 3", "Temple of Time.", y(q[MIRROR] & 4)),
                Row("ms_4", "Mirror Shard 4", "City in the Sky.", y(q[MIRROR] & 8)),
            ]),
            Section("items", "Items", "view-grid-symbolic",
                    [Row(f"it_{i:02x}", n, h, y(got(i))) for i, n, h in ITEM_LIST]),
            Section("gear", "Equipment & Upgrades", "go-up-symbolic",
                    [Row(f"it_{i:02x}", n, h, y(got(i))) for i, n, h in GEAR]),
            Section("bugs", "Golden Bugs", "emoji-nature-symbolic", bug_rows,
                    intro="All 24 Golden Bugs, a male and a female of each kind."),
            Section("poes", "Poe Souls", "weather-clear-night-symbolic", [
                Row(f"po_{k + 1}", f"Poe Soul {k + 1}", "", y(k < poes)) for k in range(60)
            ], intro=f"{poes} of 60 Poe Souls. The save only keeps a count, so they aren't named. "
                     "Bring them to Jovani in Castle Town."),
            Section("letters", "Letters", "mail-unread-symbolic", [
                Row(f"le_{k + 1}", f"Letter {k + 1}", "", y(k < letters)) for k in range(16)
            ], intro=f"{letters} of 16 letters from the postman."),
            Section("bottles", "Bottles", "applications-science-symbolic",
                    [Row(f"bt_{k + 1}", f"Bottle {k + 1}", "", y(k < bottles)) for k in range(4)]),
        ]
        res.footnote = ("Not tracked yet: individual Pieces of Heart, Hidden Skills and the Cave of Ordeals. "
                        "Wii and HD saves aren't supported.")
        return res
