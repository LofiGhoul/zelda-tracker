"""The Minish Cap (Game Boy Advance).

Save layout from zeldaret/tmc (include/save.h, src/save.c): an 8 KB EEPROM with the
signature "AGBZELDA:THE MINISH CAP:ZELDA 5" at $0000/$1000 and three $500-byte
SaveFile structs at $0080/$0580/$0A80 (backups at $1080/$1580/$1A80).

Figurines, Kinstone fusions and the inventory are stored as plain bitfields, so those
are exact. Heart Pieces have no per-location record we can name, so hearts are shown
as a total.
"""

from __future__ import annotations

from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef, popcount

SIGNATURE = b"AGBZELDA:THE MINISH CAP:ZELDA"
SLOTS = (0x080, 0x580, 0xA80)
BACKUPS = (0x1080, 0x1580, 0x1A80)
SIZE = 0x500

STATS = 0xA8          # Stats struct
FIGURINES = 0xD0      # 36-byte bitset
INVENTORY = 0xF2      # 2 bits per item id
KINSTONES = 0x114     # KinstoneSave


def _unswizzle(data: bytes) -> bytes:
    """Some emulators store EEPROM with every 8-byte block byte-reversed."""
    return b"".join(data[i:i + 8][::-1] for i in range(0, len(data), 8))


def _normalize(data: bytes) -> bytes | None:
    if len(data) not in (0x2000, 0x8000, 0x10000, 0x20000):
        return None
    for d in (data, _unswizzle(data)):
        if d[:len(SIGNATURE)] == SIGNATURE or d[0x1000:0x1000 + len(SIGNATURE)] == SIGNATURE:
            return d
    return None


def _slot_ok(d: bytes, base: int) -> bool:
    if len(d) < base + SIZE:
        return False
    blob = d[base:base + SIZE]
    if not any(blob) or blob.count(0xFF) > SIZE - 16:
        return False
    max_hp = blob[STATS + 3]
    return 24 <= max_hp <= 160 and max_hp % 8 == 0


def _find_slots(d: bytes) -> list[tuple[int, int]]:
    out = []
    for i, (a, b) in enumerate(zip(SLOTS, BACKUPS)):
        for base in (a, b):
            if _slot_ok(d, base):
                out.append((i, base))
                break
    return out


ITEMS = [  # (item id, name, hint)
    (0x01, "Smith's Sword", "From the Smith at the start."),
    (0x07, "Bombs", ""),
    (0x09, "Bow", ""),
    (0x0B, "Boomerang", ""),
    (0x0D, "Shield", "Stockwell's shop in Hyrule Town."),
    (0x0F, "Lamp", "Temple of Droplets."),
    (0x11, "Gust Jar", "Deepwood Shrine."),
    (0x12, "Cane of Pacci", "Cave of Flames."),
    (0x13, "Mole Mitts", "Fortress of Winds."),
    (0x14, "Roc's Cape", "Palace of Winds."),
    (0x15, "Pegasus Boots", ""),
    (0x17, "Ocarina of Wind", ""),
    (0x44, "Grip Ring", ""),
    (0x45, "Power Bracelets", ""),
    (0x46, "Flippers", ""),
    (0x67, "Kinstone Bag", ""),
]
UPGRADED = [
    (0x02, "White Sword", "Infuse the Earth Element at the Elemental Sanctuary."),
    (0x03, "White Sword (two elements)", "Infuse the Fire Element."),
    (0x04, "White Sword (three elements)", "Infuse the Water Element."),
    (0x06, "Four Sword", "Infuse the Wind Element."),
    (0x08, "Remote Bombs", ""),
    (0x0A, "Light Arrows", ""),
    (0x0C, "Magical Boomerang", ""),
    (0x0E, "Mirror Shield", "From Biggoron."),
]
ELEMENTS = [
    (0x40, "Earth Element", "Deepwood Shrine."),
    (0x41, "Fire Element", "Cave of Flames."),
    (0x42, "Water Element", "Temple of Droplets."),
    (0x43, "Wind Element", "Palace of Winds."),
]
SCROLLS = [
    (0x48, "Spin Attack"), (0x49, "Roll Attack"), (0x4A, "Dash Attack"), (0x4B, "Rock Breaker"),
    (0x4C, "Sword Beam"), (0x4D, "Great Spin Attack"), (0x4E, "Down Thrust"), (0x4F, "Peril Beam"),
    (0x73, "Fast Spin Scroll"), (0x74, "Fast Split Scroll"), (0x75, "Long Spin"),
]
BUTTERFLIES = [(0x70, "Arrow Butterfly"), (0x71, "Digging Butterfly"), (0x72, "Swim Butterfly")]


class MinishCap(Game):
    id, title, short, platform = "tmc", "The Minish Cap", "TMC", "Game Boy Advance"
    file_help = "the .sav file your GBA emulator writes next to the ROM"

    def detect(self, path: Path, data: bytes) -> bool:
        d = _normalize(data)
        return d is not None and bool(_find_slots(d))

    def slots(self, path: Path) -> list[SlotRef]:
        d = _normalize(path.read_bytes()) or b""
        return [SlotRef(path, i) for i, _b in _find_slots(d)]

    def read(self, slot: SlotRef) -> Result:
        d = _normalize(slot.path.read_bytes())
        found = dict(_find_slots(d or b""))
        if slot.index not in found:
            raise SaveError(f"File {(slot.index or 0) + 1} in {slot.path.name} is empty.")
        s = d[found[slot.index]:found[slot.index] + SIZE]
        y = lambda ok: "yes" if ok else None  # noqa: E731

        def inv(item: int) -> bool:
            return bool(s[INVENTORY + (item >> 2)] >> ((item & 3) * 2) & 3)

        name = "".join(chr(b) for b in s[0x80:0x86] if 0x20 <= b < 0x7F).strip() or "(no name)"
        max_hp = s[STATS + 3]
        hearts, pieces = max_hp // 8, s[STATS + 1] & 3
        res = Result(self, slot, name, hearts, pieces)

        extra = hearts - 3
        heart_sec = Section("hearts", "Hearts", None, [
            Row(f"ht_{k + 4}", f"Heart {k + 4}", "", y(k < extra)) for k in range(17)
        ], intro=(f"{hearts} of 20 hearts, plus {pieces}/4 toward the next. 6 come from bosses and "
                  "11 from the 44 Pieces of Heart; the save doesn't record which pieces you found."))

        figs = [(n, bool(s[FIGURINES + (n >> 3)] >> (n & 7) & 1)) for n in range(1, 137)]
        fig_count = sum(ok for _n, ok in figs)
        fig_sec = Section("figurines", "Figurines", "applications-games-symbolic", [
            Row(f"fg_{n}", f"Figurine #{n}", "", y(ok), group=f"#{(n - 1) // 20 * 20 + 1}–{min((n - 1) // 20 * 20 + 20, 136)}")
            for n, ok in figs
        ], intro=f"{fig_count} of 136 figurines. Buy them at Carlov's gallery in Hyrule Town "
                 "with Mysterious Shells.")

        # KinstoneSave: fusedCount at +3, fusedKinstones bitfield (13 bytes) at +0x12D
        fused_bits = popcount(int.from_bytes(s[KINSTONES + 0x12D:KINSTONES + 0x12D + 13], "little"))
        fused = min(100, max(fused_bits, s[KINSTONES + 3]))
        fusion_sec = Section("fusions", "Kinstone Fusions", "emblem-shared-symbolic", [
            Row(f"kf_{k + 1}", f"Fusion {k + 1}", "", y(k < fused)) for k in range(100)
        ], intro=f"{fused} of 100 fusions. The save stores them by fusion id, so they're "
                 "counted rather than named.")

        stats = s[STATS:STATS + 0x24]
        wallet, bombbag, quiver = stats[0], stats[6], stats[7]
        bottles = sum(inv(b) for b in range(0x1C, 0x20))

        res.sections = [
            heart_sec,
            Section("elements", "Elements", "starred-symbolic",
                    [Row(f"el_{i:02x}", n, h, y(inv(i))) for i, n, h in ELEMENTS]),
            Section("items", "Items", "view-grid-symbolic",
                    [Row(f"it_{i:02x}", n, h, y(inv(i))) for i, n, h in ITEMS]),
            Section("upgrades", "Upgrades", "go-up-symbolic",
                    [Row(f"it_{i:02x}", n, h, y(inv(i))) for i, n, h in UPGRADED] + [
                        Row("up_wallet1", "Wallet upgrade 1", "", y(wallet >= 1)),
                        Row("up_wallet2", "Wallet upgrade 2", "", y(wallet >= 2)),
                        Row("up_wallet3", "Wallet upgrade 3", "", y(wallet >= 3)),
                        Row("up_bombs1", "Bomb Bag upgrade 1", "", y(bombbag >= 2)),
                        Row("up_bombs2", "Bomb Bag upgrade 2", "", y(bombbag >= 3)),
                        Row("up_bombs3", "Bomb Bag upgrade 3", "", y(bombbag >= 4)),
                        Row("up_quiver1", "Quiver upgrade 1", "", y(quiver >= 2)),
                        Row("up_quiver2", "Quiver upgrade 2", "", y(quiver >= 3)),
                    ]),
            Section("scrolls", "Tiger Scrolls", "accessories-dictionary-symbolic",
                    [Row(f"sc_{i:02x}", n, "", y(inv(i))) for i, n in SCROLLS]),
            Section("butterflies", "Butterflies", "emoji-nature-symbolic",
                    [Row(f"bf_{i:02x}", n, "", y(inv(i))) for i, n in BUTTERFLIES]),
            Section("bottles", "Bottles", "applications-science-symbolic",
                    [Row(f"bt_{k + 1}", f"Bottle {k + 1}", "", y(k < bottles)) for k in range(4)]),
            fig_sec,
            fusion_sec,
        ]
        res.footnote = ("Not tracked: individual Piece of Heart locations (the save keeps only "
                        "the total), Mysterious Shells, small keys and dungeon maps.")
        return res
