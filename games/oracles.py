"""Oracle of Seasons and Oracle of Ages (Game Boy Color).

Save layout from Drenn1/oracles-disasm (code/fileManagement.s, include/wram.s):
three files of $550 bytes at SRAM $A010/$A560/$AAB0 (backups at $B000/$B550/$BAA0),
each a copy of WRAM $C5B0-$CAFF with a checksum, then "Z11216-0" (Seasons) or
"Z21216-0" (Ages). Room flags: bit $20 = item taken / chest opened.

Heart pieces: only some have a flag we can name (chests, Maple, the gasha spot and
the hidden shops). The rest are counted from your heart total.
"""

from __future__ import annotations

from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef, popcount

FILE_START = 0xC5B0
FILE_SIZE = 0x550
SLOTS = (0x10, 0x560, 0xAB0)
BACKUPS = (0x1000, 0x1550, 0x1AA0)

RING_NAMES = [
    "Friendship Ring", "Power Ring L-1", "Power Ring L-2", "Power Ring L-3",
    "Armor Ring L-1", "Armor Ring L-2", "Armor Ring L-3", "Red Ring", "Blue Ring",
    "Green Ring", "Cursed Ring", "Expert's Ring", "Blast Ring", "Rang Ring L-1",
    "GBA Time Ring", "Maple's Ring", "Steadfast Ring", "Pegasus Ring", "Toss Ring",
    "Heart Ring L-1", "Heart Ring L-2", "Swimmer's Ring", "Charge Ring", "Light Ring L-1",
    "Light Ring L-2", "Bomber's Ring", "Green Luck Ring", "Blue Luck Ring", "Gold Luck Ring",
    "Red Luck Ring", "Green Holy Ring", "Blue Holy Ring", "Red Holy Ring", "Snowshoe Ring",
    "Roc's Ring", "Quicksand Ring", "Red Joy Ring", "Blue Joy Ring", "Gold Joy Ring",
    "Green Joy Ring", "Discovery Ring", "Rang Ring L-2", "Octo Ring", "Moblin Ring",
    "Like Like Ring", "Subrosian Ring", "First Gen Ring", "Spin Ring", "Bombproof Ring",
    "Energy Ring", "Double-Edged Ring", "GBA Nature Ring", "Slayer's Ring", "Rupee Ring",
    "Victory Ring", "Sign Ring", "Hundredth Ring", "Whisp Ring", "Gasha Ring", "Peace Ring",
    "Zora Ring", "Fist Ring", "Whimsical Ring", "Protection Ring",
]
assert len(RING_NAMES) == 64


class _View:
    def __init__(self, data: bytes, base: int, ages: bool):
        self.d, self.b, self.ages = data, base, ages

    def u8(self, addr: int) -> int:
        return self.d[self.b + addr - FILE_START]

    def a(self, ages_addr: int, seasons_addr: int) -> int:
        return self.u8(ages_addr if self.ages else seasons_addr)

    def bit(self, addr: int, n: int) -> bool:
        return bool(self.u8(addr + (n >> 3)) >> (n & 7) & 1)

    def room(self, room: int, mask: int = 0x20) -> bool:
        group, r = room >> 8, room & 0xFF
        if self.ages:
            table = (0xC7, 0xC8, 0xC7, 0xC8, 0xC9, 0xCA, 0xC9, 0xCA)[group]
        else:
            table = (0xC7, 0xC8, 0xC8, 0xC8, 0xC9, 0xCA, 0xC9, 0xCA)[group]
        return bool(self.u8(table << 8 | r) & mask)

    def treasure(self, tid: int) -> bool:
        return self.bit(0xC69A if self.ages else 0xC692, tid)


def _find_slots(data: bytes, magic: bytes) -> list[int]:
    out = []
    for i, (main, backup) in enumerate(zip(SLOTS, BACKUPS)):
        for base in (main, backup):
            tag = data[base + 2:base + 10]
            if len(data) >= base + FILE_SIZE and tag in (magic, magic[::-1]):
                out.append((i, base))
                break
    return out


def _name(raw: bytes) -> str:
    return "".join(chr(b) if 0x20 <= b < 0x7F else "" for b in raw.split(b"\0")[0]).strip()


class _Oracle(Game):
    platform = "Game Boy Color"
    file_help = "the .sav (or .srm) file your Game Boy emulator writes next to the ROM"
    magic = b""
    ages = False

    def detect(self, path: Path, data: bytes) -> bool:
        return len(data) in (0x2000, 0x8000) and bool(_find_slots(data, self.magic))

    def slots(self, path: Path) -> list[SlotRef]:
        return [SlotRef(path, i) for i, _b in _find_slots(path.read_bytes(), self.magic)]

    def read(self, slot: SlotRef) -> Result:
        data = slot.path.read_bytes()
        found = dict(_find_slots(data, self.magic))
        if slot.index not in found:
            raise SaveError(f"File {(slot.index or 0) + 1} in {slot.path.name} is empty.")
        v = _View(data, found[slot.index], self.ages)
        y = lambda ok: "yes" if ok else None  # noqa: E731

        name = _name(bytes(v.u8(0xC602 + i) for i in range(6))) or "(no name)"
        linked = bool(v.a(0xC612, 0xC612))
        max_hp = v.a(0xC6AB, 0xC6A3)
        hearts, in_progress = max_hp // 4, v.a(0xC6AC, 0xC6A4) & 3
        essences = v.a(0xC6BF, 0xC6BB)
        res = Result(self, slot, name, hearts, in_progress)
        if linked:
            res.tags.append("Linked game")
        if v.a(0xC613, 0xC613):
            res.tags.append("Hero's quest")

        # ---- heart containers (room flag, or inferred from the essence) -------------
        boss_rows = []
        for i, (room, boss) in enumerate(self.bosses):
            st = "yes" if v.room(room) else ("inferred" if essences >> i & 1 else None)
            boss_rows.append(Row(f"hc_{i + 1}", f"{boss} Heart Container", f"Level {i + 1} dungeon.", st))
        containers = sum(1 for r in boss_rows if r.ok)

        # ---- heart pieces --------------------------------------------------------------
        known = [Row(f"hp_{key}", n, hint, y(test(v)), group="Pieces with a flag in the save")
                 for key, n, hint, test in self.pieces]
        start = 4 if linked else 3
        total_pieces = min(12, max(0, (hearts - start - containers) * 4 + in_progress))
        others_got = max(0, total_pieces - sum(1 for r in known if r.ok))
        n_other = 12 - len(known)
        others = [Row(f"hp_other{i + 1}", f"Other Piece of Heart {i + 1}",
                      "Counted from your hearts; the save has no flag that names it.",
                      "inferred" if i < others_got else None, group="Counted from your hearts")
                  for i in range(n_other)]
        hp = Section("hearts", "Pieces of Heart", None, known + others)
        hp.intro = (f"Your hearts show {total_pieces} of 12 pieces. The game only keeps a "
                    f"named flag for {len(known)} of them; the rest are counted.")

        rings = [Row(f"rg_{i:02x}", n, "", y(v.bit(0xC616, i))) for i, n in enumerate(RING_NAMES)]

        res.sections = [
            hp,
            Section("bosses", "Heart Containers", "emblem-favorite-symbolic", boss_rows),
            Section("essences", "Essences", "starred-symbolic", [
                Row(f"es_{i + 1}", n, f"Level {i + 1} dungeon.", y(essences >> i & 1))
                for i, n in enumerate(self.essences)
            ]),
            Section("items", "Items", "view-grid-symbolic", self.items(v)),
            Section("upgrades", "Upgrades", "go-up-symbolic", self.upgrades(v)),
            *self.extra_sections(v),
            Section("rings", "Rings", "emblem-ok-symbolic", rings,
                    intro=f"{sum(r.ok for r in rings)} of 64 rings. Some only come from linked "
                          "games or the Ring secrets, and a few were GBA-only."),
        ]
        res.footnote = ("Not tracked: the trading sequence, gasha trees, secrets and small keys. "
                        "Heart Containers you skipped are shown as Inferred if you have that dungeon's essence.")
        return res

    # shared item checks: (name, hint, test)
    def _common_items(self, v: _View) -> list[Row]:
        y = lambda ok: "yes" if ok else None  # noqa: E731
        sword = v.a(0xC6B2, 0xC6AC)
        shield = v.a(0xC6AF, 0xC6A9)
        return [
            Row("it_sword", "Wooden Sword", "The first sword.", y(sword >= 1)),
            Row("it_shield", "Wooden Shield", "Buy or find the shield.", y(shield >= 1)),
            Row("it_bombs", "Bombs", "", y(v.treasure(0x03))),
            Row("it_satchel", "Seed Satchel", "", y(v.treasure(0x19))),
            Row("it_ember", "Ember Seeds", "", y(v.treasure(0x20))),
            Row("it_scent", "Scent Seeds", "", y(v.treasure(0x21))),
            Row("it_pegasus", "Pegasus Seeds", "", y(v.treasure(0x22))),
            Row("it_gale", "Gale Seeds", "", y(v.treasure(0x23))),
            Row("it_mystery", "Mystery Seeds", "", y(v.treasure(0x24))),
            Row("it_bracelet", "Power Bracelet", "", y(v.treasure(0x16))),
            Row("it_shovel", "Shovel", "", y(v.treasure(0x15))),
            Row("it_feather", "Roc's Feather", "", y(v.treasure(0x17))),
            Row("it_flute", "Animal flute", "From Ricky, Dimitri or Moosh.", y(v.treasure(0x0E))),
            Row("it_ringbox", "Ring Box", "", y(v.treasure(0x2C))),
            Row("it_bombchus", "Bombchus", "", y(v.treasure(0x0D))),
            Row("it_biggoron", "Biggoron's Sword", "End of the trading sequence.", y(v.treasure(0x0C))),
        ]

    def _common_upgrades(self, v: _View) -> list[Row]:
        y = lambda ok: "yes" if ok else None  # noqa: E731
        sword, shield = v.a(0xC6B2, 0xC6AC), v.a(0xC6AF, 0xC6A9)
        satchel, ringbox = v.a(0xC6B4, 0xC6AE), v.a(0xC6CC, 0xC6C6)
        return [
            Row("up_sword2", "Noble Sword", "", y(sword >= 2)),
            Row("up_sword3", "Master Sword", "", y(sword >= 3)),
            Row("up_shield2", "Iron Shield", "", y(shield >= 2)),
            Row("up_shield3", "Mirror Shield", "", y(shield >= 3)),
            Row("up_satchel2", "Seed Satchel L-2", "", y(satchel >= 2)),
            Row("up_satchel3", "Seed Satchel L-3", "", y(satchel >= 3)),
            Row("up_bombs", "Bigger Bomb Bag", "", y(v.a(0xC6B1, 0xC6AB) > 0x10)),
            Row("up_ringbox2", "Ring Box L-2", "", y(ringbox >= 2)),
            Row("up_ringbox3", "Ring Box L-3", "", y(ringbox >= 3)),
        ]

    def extra_sections(self, v: _View) -> list[Section]:
        return []


class OracleOfSeasons(_Oracle):
    id, title, short = "oos", "Oracle of Seasons", "OoS"
    magic = b"Z11216-0"
    ages = False
    bosses = [(0x412, "Aquamentus"), (0x429, "Dodongo"), (0x453, "Mothula"), (0x45F, "Gohma"),
              (0x48C, "Digdogger"), (0x4D5, "Manhandla"), (0x550, "Gleeok"), (0x564, "Medusa Head")]
    essences = ["Fertile Soil", "Gift of Time", "Bright Sun", "Soothing Rain",
                "Nurturing Warmth", "Blowing Wind", "Seed of Life", "Changing Seasons"]
    pieces = [
        ("moblin_keep", "Moblin's Keep chest", "In a chest inside Moblin's Keep.", lambda v: v.room(0x005B)),
        ("eyeglass_cave", "Dry Eyeglass Lake cave", "Chest in the east cave of the dried-up lake.",
         lambda v: v.room(0x05C0)),
        ("subrosia_market", "Subrosian Market", "Trade for it in the Subrosian Market.",
         lambda v: bool(v.u8(0xC642) & 0x02)),
        ("maple", "Maple", "Bump into Maple and pick it up from what she drops.",
         lambda v: bool(v.u8(0xC641) & 0x80)),
        ("gasha", "Gasha tree", "From one of the gasha nuts you harvest.",
         lambda v: bool(v.u8(0xC649) & 0x02)),
    ]

    def items(self, v):
        y = lambda ok: "yes" if ok else None  # noqa: E731
        return self._common_items(v) + [
            Row("it_rod", "Rod of Seasons", "", y(v.treasure(0x07))),
            Row("it_boomerang", "Boomerang", "", y(v.treasure(0x06))),
            Row("it_slingshot", "Slingshot", "", y(v.treasure(0x13))),
            Row("it_magnet", "Magnetic Gloves", "", y(v.treasure(0x08))),
            Row("it_flippers", "Zora's Flippers", "", y(v.treasure(0x2E))),
        ]

    def upgrades(self, v):
        y = lambda ok: "yes" if ok else None  # noqa: E731
        return self._common_upgrades(v) + [
            Row("up_boomerang2", "Magical Boomerang", "", y(v.u8(0xC6B1) >= 2)),
            Row("up_slingshot2", "Hyper Slingshot", "", y(v.u8(0xC6B3) >= 2)),
            Row("up_feather2", "Roc's Cape", "", y(v.u8(0xC6B4) >= 2)),
        ]

    def extra_sections(self, v):
        seasons = v.u8(0xC6B0)
        return [Section("seasons", "Seasons", "weather-few-clouds-symbolic", [
            Row(f"se_{n.lower()}", f"Spirit of {n}", "", "yes" if seasons >> i & 1 else None)
            for i, n in enumerate(("Spring", "Summer", "Autumn", "Winter"))
        ])]


class OracleOfAges(_Oracle):
    id, title, short = "ooa", "Oracle of Ages", "OoA"
    magic = b"Z21216-0"
    ages = True
    bosses = [(0x413, "Pumpkin Head"), (0x62B, "Head Thwomp"), (0x44A, "Shadow Hag"),
              (0x46B, "Eyesoar"), (0x4BF, "Smog"), (0x536, "Octogon"), (0x562, "Plasmarine"),
              (0x578, "Ramrock")]
    essences = ["Eternal Spirit", "Ancient Wood", "Echoing Howl", "Burning Flame",
                "Sacred Soil", "Lonely Peak", "Rolling Sea", "Falling Star"]
    pieces = [
        ("crescent", "Under Crescent Island", "Chest in the cave under Crescent Island.",
         lambda v: v.room(0x03FD)),
        ("hidden_shop", "Hidden shop", "Buy it in the hidden shop in Lynna City.",
         lambda v: bool(v.u8(0xC643) & 0x40)),
        ("maple", "Maple", "Bump into Maple and pick it up from what she drops.",
         lambda v: bool(v.u8(0xC644) & 0x80)),
        ("gasha", "Gasha tree", "From one of the gasha nuts you harvest.",
         lambda v: bool(v.u8(0xC64C) & 0x02)),
    ]

    def items(self, v):
        y = lambda ok: "yes" if ok else None  # noqa: E731
        return self._common_items(v) + [
            Row("it_shooter", "Seed Shooter", "", y(v.treasure(0x0F))),
            Row("it_hook", "Switch Hook", "", y(v.treasure(0x0A))),
            Row("it_cane", "Cane of Somaria", "", y(v.treasure(0x04))),
            Row("it_harp", "Harp of Ages", "", y(v.treasure(0x11))),
            Row("it_suit", "Mermaid Suit", "", y(v.treasure(0x4A))),
        ]

    def upgrades(self, v):
        y = lambda ok: "yes" if ok else None  # noqa: E731
        return self._common_upgrades(v) + [
            Row("up_hook2", "Long Hook", "", y(v.u8(0xC6B6) >= 2)),
            Row("up_bracelet2", "Power Glove", "", y(v.u8(0xC6B8) >= 2)),
        ]

    def extra_sections(self, v):
        return [Section("tunes", "Harp tunes", "audio-x-generic-symbolic", [
            Row("tu_echoes", "Tune of Echoes", "", "yes" if v.treasure(0x25) else None),
            Row("tu_currents", "Tune of Currents", "", "yes" if v.treasure(0x26) else None),
            Row("tu_ages", "Tune of Ages", "", "yes" if v.treasure(0x27) else None),
        ])]
