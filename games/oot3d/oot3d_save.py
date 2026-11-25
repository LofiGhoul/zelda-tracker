"""Ocarina of Time 3D save parser: which Pieces of Heart a save slot has collected.

A slot file holds the game's SaveContext (little-endian), as dumped from a 3DS
with Checkpoint/JKSM or taken from Citra/Azahar/Lime3DS. The parser finds the
"ZELDAZ" marker (SaveContext+0x30), so a small header in front doesn't matter.

Layout sources:
  * gamestabled/OoT3D_Randomizer code/include/z3D/z3D.h: SaveContext offsets
  * OoT3D_Randomizer source/item_location.cpp: scene and flag for every check
  * OoT3D_Randomizer code/src/spoiler_data.c: how each kind of flag is read on
    the 3DS (itemGetInf and infTable are tested with their bytes swapped)
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .checklist import Category, Check, SaveView, build_categories
    from .guide import STEPS
except ImportError:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from checklist import Category, Check, SaveView, build_categories
    from guide import STEPS

MAGIC = b"ZELDAZ"
MAGIC_OFF = 0x30          # SaveContext.newf
MIN_SIZE = 0x14DC         # a real slot file is 0x14DC bytes (through the checksum)

OFF_NAME = 0x1C           # s16[8], UTF-16LE
OFF_NAME_LEN = 0x2C
OFF_HEART_CAP = 0x42      # s16, 0x10 per heart
OFF_MQ = 0x0E
OFF_QUEST = 0xBC          # u32; heart pieces in the top byte

TOTAL_PIECES = 36

# Boss rooms: the Heart Container sets collectible flag 0x1F.
BOSS_ROOMS = {
    0x11: "Gohma", 0x12: "King Dodongo", 0x13: "Barinade", 0x14: "Phantom Ganon",
    0x15: "Volvagia", 0x16: "Morpha", 0x17: "Twinrova", 0x18: "Bongo Bongo",
}

# A flag check, read by SaveView.flag():
#   ("coll", scene, bit) ("chest", scene, bit) ("scrub", scene, bit)
#   ("evt", flag) ("igi", slot) ("inf", index, bit) ("fish", bit) ("gs", area, mask)
Flag = tuple


@dataclass(frozen=True)
class Piece:
    id: str
    region: str
    name: str
    hint: str
    flags: tuple[Flag, ...]          # any one set => collected

    @property
    def steps(self) -> tuple[str, ...]:
        return STEPS.get(self.id, ())


REGIONS = [
    "Kokiri Forest & Lost Woods",
    "Hyrule Field & Market",
    "Lon Lon Ranch",
    "Kakariko & Graveyard",
    "Death Mountain",
    "Zora's River, Domain & Fountain",
    "Lake Hylia",
    "Gerudo Valley & Desert",
    "Dungeons",
]
R = REGIONS

PIECES: list[Piece] = [
    # ---- Kokiri Forest & Lost Woods -----------------------------------------
    Piece("lw_skull_kid", R[0], "Skull Kid's song",
          "Child: play Saria's Song for the Skull Kid on the stump.", (("igi", 30),)),
    Piece("lw_memory_game", R[0], "Ocarina memory game",
          "Child: copy the Skull Kids' tunes in the Lost Woods.", (("igi", 31),)),
    # ---- Hyrule Field & Market ----------------------------------------------
    Piece("hf_tektite_grotto", R[1], "Tektite grotto",
          "Adult: dive to the bottom of a hidden water grotto in Hyrule Field.",
          (("coll", 0x3E, 1),)),
    Piece("hf_scrub_grotto", R[1], "Deku Scrub grotto",
          "Buy it from a Business Scrub in a hidden Hyrule Field grotto.", (("scrub", 0x10, 3),)),
    Piece("mk_treasure_game", R[1], "Treasure Chest Shop",
          "Child at night: win the Market's Treasure Chest game.", (("igi", 19),)),
    Piece("mk_bombchu_bowling", R[1], "Bombchu Bowling",
          "Child: win the Bombchu Bowling Alley when the prize is a Piece of Heart.",
          (("igi", 26),)),
    Piece("mk_lost_dog", R[1], "Richard the lost dog",
          "Child at night: bring Richard back to his owner in the back alley.",
          (("inf", 0x19, 9),)),
    # ---- Lon Lon Ranch ------------------------------------------------------
    Piece("llr_tower", R[2], "Ranch silo",
          "Child: crawl through the gap between the crates in the silo.", (("coll", 0x4C, 1),)),
    # ---- Kakariko & Graveyard -----------------------------------------------
    Piece("kak_impa_house", R[3], "Impa's house cow pen",
          "Climb onto the roofs and drop into the cow pen at the back of Impa's house.",
          (("coll", 0x37, 1),)),
    Piece("kak_windmill", R[3], "Windmill ledge",
          "On a high ledge inside the windmill.", (("coll", 0x48, 1),)),
    Piece("kak_man_on_roof", R[3], "Man on the roof",
          "Talk to the man sitting on the roof of Impa's house.", (("igi", 29),)),
    Piece("kak_50_skulltulas", R[3], "50 Gold Skulltulas",
          "Bring 50 Gold Skulltula tokens to the House of Skulltula.", (("evt", 0xDE),)),
    Piece("gy_redead_grave", R[3], "Redead grave chest",
          "Play the Sun's Song inside the grave full of Redeads.", (("chest", 0x3F, 0),)),
    Piece("gy_dampe_race", R[3], "Dampé's race",
          "Adult: race Dampé's ghost again and finish in under a minute.", (("coll", 0x48, 7),)),
    Piece("gy_ledge", R[3], "Graveyard ledge",
          "In a crate on a high ledge at the back of the Graveyard.", (("coll", 0x53, 4),)),
    Piece("gy_dampe_dig", R[3], "Dampé's gravedigging tour",
          "Child at night: pay Dampé to dig until he finds a Piece of Heart.", (("igi", 20),)),
    # ---- Death Mountain -----------------------------------------------------
    Piece("dmt_above_cavern", R[4], "Above Dodongo's Cavern",
          "On top of the entrance to Dodongo's Cavern.", (("coll", 0x60, 0x1E),)),
    Piece("gc_spinning_pot", R[4], "Goron City spinning pot",
          "Child: get a bomb into the big spinning pot when it shows the happy face.",
          (("coll", 0x62, 0x1F),)),
    Piece("dmc_wall", R[4], "Crater wall alcove",
          "In an alcove on the crater wall near the Death Mountain Trail entrance.",
          (("coll", 0x61, 2),)),
    Piece("dmc_volcano", R[4], "Top of the volcano",
          "Plant a bean in the crater as a child, then ride it up as an adult.", (("coll", 0x61, 8),)),
    # ---- Zora's River, Domain & Fountain ------------------------------------
    Piece("zr_frogs_storms", R[5], "Frogs in the rain",
          "Child: play the Song of Storms for the frogs on Zora's River.", (("evt", 0xD6),)),
    Piece("zr_frogs_game", R[5], "Frogs' ocarina game",
          "Child: play the frogs all five songs, then beat their game.", (("evt", 0xD0),)),
    Piece("zr_near_grotto", R[5], "Pillar near the open grotto",
          "On top of a rock pillar near the start of Zora's River.", (("coll", 0x54, 4),)),
    Piece("zr_near_domain", R[5], "Ledge by the waterfall",
          "On a ledge high up near the waterfall to Zora's Domain.", (("coll", 0x54, 0x0B),)),
    Piece("zd_torches", R[5], "Zora's Domain torches",
          "Child: light every torch in Zora's Domain to make a chest appear.", (("chest", 0x58, 0),)),
    Piece("zf_iceberg", R[5], "Iceberg",
          "Adult: on an iceberg in the frozen Zora's Fountain.", (("coll", 0x59, 1),)),
    Piece("zf_bottom", R[5], "Bottom of the fountain",
          "Adult: sink to the floor of Zora's Fountain with the Iron Boots.", (("coll", 0x59, 0x14),)),
    # ---- Lake Hylia ---------------------------------------------------------
    Piece("lh_lab_roof", R[6], "Laboratory roof",
          "Adult: ride the bean plant to the top of the Lakeside Laboratory.", (("coll", 0x57, 0x1E),)),
    Piece("lh_lab_dive", R[6], "Laboratory dive",
          "Adult: dive to the bottom of the lab's pool with the Gold Scale.", (("igi", 24),)),
    Piece("lh_child_fishing", R[6], "Fishing Pond (child)",
          "Child: catch a fish of 10 pounds or more.", (("fish", 2),)),
    # ---- Gerudo Valley & Desert ---------------------------------------------
    Piece("gv_waterfall", R[7], "Waterfall ledge",
          "On a ledge down the waterfall below the Gerudo Valley bridge.", (("coll", 0x5A, 1),)),
    Piece("gv_crate", R[7], "Crate by the river",
          "Child: in a crate at the bottom of Gerudo Valley.", (("coll", 0x5A, 2),)),
    Piece("gf_rooftop_chest", R[7], "Fortress rooftop chest",
          "Adult: chest on the highest roof of Gerudo's Fortress.", (("chest", 0x5D, 0),)),
    Piece("gf_archery_1000", R[7], "Horseback archery: 1,000 points",
          "Adult: score 1,000 points at the Gerudo horseback archery range.",
          (("inf", 0x19, 8),)),
    Piece("colossus_ledge", R[7], "Desert Colossus ledge",
          "Plant a bean at the Colossus as a child, then ride it as an adult.",
          (("coll", 0x5C, 0x0D),)),
    # ---- Dungeons -----------------------------------------------------------
    Piece("ice_cavern", R[8], "Ice Cavern",
          "Melt the red ice around it with Blue Fire.", (("coll", 0x09, 1),)),
]

assert len(PIECES) == TOTAL_PIECES, len(PIECES)
assert set(STEPS) == {p.id for p in PIECES}, set(STEPS) ^ {p.id for p in PIECES}


UNSURE_FLAGS = ("gy_dampe_dig", "hf_scrub_grotto")


class SaveError(ValueError):
    pass


@dataclass
class SlotResult:
    path: Path
    player_name: str
    master_quest: bool
    heart_containers: int          # total hearts (incl. the starting 3)
    pieces_in_progress: int        # 0-3 towards the next heart
    boss_containers: list[str]
    expected_total: int            # pieces collected, worked out from hearts
    collected: dict[str, str] = field(default_factory=dict)  # id -> "yes"
    # other 100% categories: (category, [(check, done, detail text)])
    categories: list[tuple[Category, list[tuple[Check, bool, str]]]] = field(default_factory=list)

    @property
    def overall(self) -> tuple[int, int]:
        """(done, total) across heart pieces and every category, each check counted once."""
        done = {f"hp_{k}" for k in self.collected}
        total = {f"hp_{p.id}" for p in PIECES}
        for _cat, rows in self.categories:
            for check, ok, _ in rows:
                total.add(check.id)
                if ok:
                    done.add(check.id)
        return len(done), len(total)

    @property
    def collected_count(self) -> int:
        return len(self.collected)

    @property
    def unexplained(self) -> int:
        """Pieces the hearts say you have that no flag accounts for."""
        return self.expected_total - self.collected_count


def find_base(data: bytes) -> int:
    """Offset of the SaveContext inside the file, or -1."""
    i = data.find(MAGIC)
    while i != -1:
        base = i - MAGIC_OFF
        if base >= 0 and len(data) - base >= MIN_SIZE:
            hc = struct.unpack_from("<h", data, base + OFF_HEART_CAP)[0]
            if 0x30 <= hc <= 0x140 and hc % 0x10 == 0:
                return base
        i = data.find(MAGIC, i + 1)
    return -1


def _pieces_in_progress(quest: int) -> int:
    top = quest >> 24
    # N64 stores 0x10 per piece in the top byte; accept a plain count too.
    return (top >> 4 if top & 0xF == 0 else top) & 3


def read_slot(path: str | Path) -> SlotResult:
    path = Path(path)
    data = path.read_bytes()
    base = find_base(data)
    if base < 0:
        if len(data) >= MIN_SIZE and not data.strip(b"\0\xff"):
            raise SaveError(f"{path.name} is an empty save slot.")
        raise SaveError(f"{path.name} isn't an Ocarina of Time 3D save slot (no 'ZELDAZ' marker).")
    view = SaveView(data, base)

    n = min(view.u8(OFF_NAME_LEN) or 8, 8)
    raw = data[base + OFF_NAME:base + OFF_NAME + 2 * n]
    name = raw.decode("utf-16le", "replace").split("\0")[0].strip()
    hearts = view.s16(OFF_HEART_CAP) >> 4
    in_progress = _pieces_in_progress(view.u32(OFF_QUEST))
    mq = bool(view.u8(OFF_MQ))

    bosses = [boss for scene, boss in BOSS_ROOMS.items() if view.flag(("coll", scene, 0x1F))]
    expected = min(TOTAL_PIECES, max(0, (hearts - 3 - len(bosses)) * 4 + in_progress))

    result = SlotResult(path, name or "(no name)", mq, hearts, in_progress, bosses, expected)
    for p in PIECES:
        if any(view.flag(f) for f in p.flags):
            result.collected[p.id] = "yes"
    # These two use flags the randomizer defines but the real game may store elsewhere (they
    # read as missing even on full-heart saves), so credit them from the heart total instead.
    spare = expected - len(result.collected)
    for pid in UNSURE_FLAGS:
        if spare <= 0:
            break
        if pid not in result.collected:
            result.collected[pid] = "inferred"
            spare -= 1

    for cat in build_categories(mq):
        rows = [(c, bool(c.test(view)), c.detail(view) if c.detail else "") for c in cat.checks]
        result.categories.append((cat, rows))
    return result


def _is_slot(p: Path) -> bool:
    try:
        return p.is_file() and find_base(p.read_bytes()) >= 0
    except OSError:
        return False


def find_slot_siblings(path: Path) -> list[Path]:
    """Every OoT3D slot file in the same folder, in name order."""
    out = [p for p in sorted(path.parent.glob("*.bin")) if _is_slot(p)]
    return out or [path]


# 3DS title IDs: JPN, USA, EUR
TITLE_IDS = ("00033400", "00033500", "00033600")


def discover_saves() -> list[Path]:
    """Look for OoT3D slots in common emulator and download locations."""
    home = Path.home()
    roots = [
        home / ".local/share/azahar-emu/sdmc",
        home / ".local/share/azaharplus-emu/sdmc",
        home / ".local/share/citra-emu/sdmc",
        home / ".local/share/lime3ds-emu/sdmc",
        home / ".local/share/Lime3DS/sdmc",
        *home.glob(".var/app/*/data/*/sdmc"),
    ]
    found: list[Path] = []
    for root in roots:
        if root.is_dir():
            for tid in TITLE_IDS:
                found += root.glob(f"Nintendo 3DS/*/*/title/00040000/{tid}/data/*/*.bin")
    for d in (home / "Downloads", home / "Documents"):
        if d.is_dir():
            found += d.glob("save*.bin")
            found += d.glob("*/save*.bin")
    good = [p for p in found if p.stat().st_size >= MIN_SIZE and _is_slot(p)]
    return sorted(set(good), key=lambda p: p.stat().st_mtime, reverse=True)


if __name__ == "__main__":
    import sys

    for arg in sys.argv[1:]:
        r = read_slot(arg)
        print(f"{r.path.name}: {r.player_name}  hearts={r.heart_containers} "
              f"+{r.pieces_in_progress}/4  bosses={len(r.boss_containers)}  mq={r.master_quest}")
        print(f"  pieces {r.collected_count}/{TOTAL_PIECES} "
              f"(expected from hearts {r.expected_total}, unexplained {r.unexplained})")
        for p in PIECES:
            print(f"  [{'x' if p.id in r.collected else ' '}] {p.region:32s} {p.name}")
        done, total = r.overall
        print(f"  overall {done}/{total}")
        for cat, rows in r.categories:
            print(f"  {cat.title}: {sum(ok for _c, ok, _d in rows)}/{len(rows)}")
