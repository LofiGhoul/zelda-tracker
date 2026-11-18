"""A Link Between Worlds (3DS): Save_0.bin / Save_1.bin / Save_2.bin.

Offsets from Brionjv's open-source ALBW save editor. A file holds three CRC32-protected
blocks; the first ($000-$DFB, CRC at $DFC) has the player data used here.

Item bytes for Ravio's gear: 0 = none, 1 = rented, 2 = owned, 3 = nice (upgraded by
Mother Maiamai). Hearts are stored in quarters.
"""

from __future__ import annotations

import re
import struct
import zlib
from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef

CRC_AT = 0xDFC
MIN_SIZE = 0x1600

RAVIO = [  # (offset, name)
    (0xCC, "Bow"), (0xCB, "Boomerang"), (0xD3, "Hookshot"), (0xCA, "Bombs"),
    (0xD0, "Fire Rod"), (0xD1, "Ice Rod"), (0xD2, "Tornado Rod"), (0xCF, "Sand Rod"),
    (0xCE, "Hammer"),
]
OTHER = [  # (offset, name, hint, owned test)
    (0xD4, "Lamp", "", 2), (0xD5, "Bug Net", "", 2), (0xCD, "Bow of Light", "", 1),
    (0xD6, "Hint Glasses", "", 2), (0xDF, "Ravio's Bracelet", "", 1), (0xE4, "Zora's Flippers", "", 1),
    (0xE8, "Pegasus Boots", "", 1), (0xE6, "Power Glove", "", 1), (0xE9, "Bee Badge", "", 1),
    (0xEE, "Stamina Scroll", "", 1), (0xEF, "Pouch", "", 1),
]


def _crc_ok(data: bytes) -> bool:
    return len(data) >= MIN_SIZE and zlib.crc32(data[:CRC_AT]) == struct.unpack_from("<I", data, CRC_AT)[0]


class LinkBetweenWorlds(Game):
    id, title, short, platform = "albw", "A Link Between Worlds", "ALBW", "3DS"
    file_help = "Save_0.bin, Save_1.bin or Save_2.bin from JKSM/Checkpoint or a 3DS emulator"

    def detect(self, path: Path, data: bytes) -> bool:
        if not MIN_SIZE <= len(data) <= 0x4000:
            return False
        named = bool(re.fullmatch(r"save_?\d\.bin", path.name, re.I))
        return _crc_ok(data) or (named and 12 <= data[0xC1] <= 80 and data[0xC1] % 4 == 0)

    def slots(self, path: Path) -> list[SlotRef]:
        sibs = sorted(p for p in path.parent.glob("*.bin")
                      if re.fullmatch(r"save_?\d\.bin", p.name, re.I) and self.detect(p, p.read_bytes()))
        return [SlotRef(p) for p in sibs] or [SlotRef(path)]

    def slot_label(self, slot: SlotRef, i: int) -> str:
        m = re.search(r"(\d)\.bin$", slot.path.name)
        return str(int(m.group(1)) + 1) if m else str(i + 1)

    def read(self, slot: SlotRef) -> Result:
        d = slot.path.read_bytes()
        if len(d) < MIN_SIZE:
            raise SaveError(f"{slot.path.name} is too small to be an ALBW save.")
        y = lambda ok: "yes" if ok else None  # noqa: E731
        name = d[0xD60:0xD60 + 20].decode("utf-16le", "replace").split("\0")[0].strip() or "(no name)"
        hearts, frags = d[0xC1] // 4, d[0xC2] & 3
        res = Result(self, slot, name, hearts, frags)
        if not _crc_ok(d):
            res.banners.append("This save's checksum doesn't match, so it may be damaged or edited.")

        extra = hearts - 3
        heart_sec = Section("hearts", "Hearts", None, [
            Row(f"ht_{k + 4}", f"Heart {k + 4}", "", y(k < extra)) for k in range(17)
        ], intro=(f"{hearts} of 20 hearts, plus {frags}/4 toward the next. 10 come from bosses and 7 from "
                  "the 28 Pieces of Heart; this tracker doesn't read which pieces you found yet."))

        res.sections = [
            heart_sec,
            Section("pendants", "Pendants", "starred-symbolic", [
                Row("pe_courage", "Pendant of Courage", "Eastern Palace.", y(d[0xE2])),
                Row("pe_power", "Pendant of Power", "House of Gales.", y(d[0xE1])),
                Row("pe_wisdom", "Pendant of Wisdom", "Tower of Hera.", y(d[0xE0])),
            ]),
            Section("ravio", "Ravio's items (owned)", "view-grid-symbolic", [
                Row(f"rv_{off:x}", n, "Buy it from Ravio (renting doesn't count).", y(d[off] >= 2),
                    "Rented" if d[off] == 1 else "") for off, n in RAVIO
            ]),
            Section("nice", "Nice items", "go-up-symbolic", [
                Row(f"ni_{off:x}", f"Nice {n}", "Bring Maiamai to Mother Maiamai (10 per upgrade).",
                    y(d[off] >= 3)) for off, n in RAVIO
            ]),
            Section("items", "Items", "applications-games-symbolic", [
                *[Row(f"it_{off:x}", n, h, y(d[off] >= need)) for off, n, h, need in OTHER],
                Row("it_titans", "Titan's Mitt", "", y(d[0xE6] >= 2)),
            ]),
            Section("bottles", "Bottles", "applications-science-symbolic", [
                Row(f"bt_{i + 1}", f"Bottle {i + 1}", "", y(d[0xDA + i] >= 2)) for i in range(5)
            ]),
        ]
        res.footnote = ("Not tracked yet: individual Pieces of Heart, Maiamai locations, the Sages and "
                        "sword/mail upgrades. The community save editor labels those bytes but doesn't "
                        "decode them, so they're left out rather than guessed.")
        return res
