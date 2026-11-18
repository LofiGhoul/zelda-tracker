"""Majora's Mask 3D save parser: which Pieces of Heart a save slot has collected.

A slot file is `saveN.bin` (0x13618 bytes, little-endian), as dumped from a 3DS
with Checkpoint/JKSM or taken from Citra/Azahar/Lime3DS.

Layout sources:
  * yellows8/mm3d_re: file header, CRC16, heart capacity at 0x13A
  * Z3DR/mm3dr common_data.h: SaveData starts at file+0x8, weekEventReg at
    SaveData+0x1248, collect register at SaveData+0x1F0
  * Per-scene flag table at SaveData+0x248: 120 scenes x 0x20 bytes, where
    word 1 = chest flags and word 4 = collectible flags (checked against real
    saves using the decomp's per-scene persistent-flag table)
  * Flag numbers per location: 2Ship2Harkinian's check table and the MM3D
    randomizer location list, checked against real saves
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

try:
    from .checklist import CATEGORIES, Category, Check, SaveView
    from .guide import STEPS
except ImportError:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from checklist import CATEGORIES, Category, Check, SaveView
    from guide import STEPS

SAVE_SIZE = 0x13618
MAGIC = b"MJR"

OFF_CRC = 0x1A88
OFF_NAME = 0x128          # UTF-16LE, 8 chars
OFF_HEART_CAP = 0x13A     # s16, 0x10 per heart
OFF_COLLECT_REG = 0x1F8   # u32; bits 0-3 remains, bits 28-31 heart pieces (0-3)
OFF_WEEK_EVENT = 0x1250
OFF_SCENE_FLAGS = 0x250
SCENE_STRIDE = 0x20
WORD_CHEST = 1
WORD_COLLECTIBLE = 4

TOTAL_PIECES = 52

# Boss rooms: the Heart Container sets collectible flag 0x1F.
BOSS_ROOMS = {0x1F: "Odolwa", 0x44: "Goht", 0x5F: "Gyorg", 0x36: "Twinmold"}

_CRC_TABLE = []
for _i in range(256):
    _c = _i
    for _ in range(8):
        _c = (_c >> 1) ^ 0xA001 if _c & 1 else _c >> 1
    _CRC_TABLE.append(_c)


def crc16(data: bytes, seed: int = 0x1017) -> int:
    crc = seed
    for b in data:
        crc = _CRC_TABLE[(b ^ crc) & 0xFF] ^ (crc >> 8)
    return crc


# A flag check: ("we", byte, mask) | ("coll", scene, bit) | ("chest", scene, bit)
Flag = tuple


@dataclass(frozen=True)
class Piece:
    id: str
    region: str
    name: str
    hint: str
    flags: tuple[Flag, ...]          # any one set => collected
    inferable: bool = False          # flag doesn't survive a cycle reset in MM3D

    @property
    def steps(self) -> tuple[str, ...]:
        return STEPS.get(self.id, ())


REGIONS = [
    "Clock Town",
    "Termina Field & Ranch",
    "Southern Swamp & Woodfall",
    "Snowhead",
    "Great Bay",
    "Ikana",
    "The Moon",
]

PIECES: list[Piece] = [
    # ---- Clock Town -------------------------------------------------------
    Piece("mayor", "Clock Town", "Mayor's Office",
          "Wear the Couple's Mask during the Mayor's meeting.", (("we", 60, 0x10),)),
    Piece("town_gallery", "Clock Town", "Town Shooting Gallery",
          "Get a perfect score at the East Clock Town gallery.", (("we", 32, 0x04),)),
    Piece("honey_darling", "Clock Town", "Honey & Darling",
          "Win their East Clock Town game on all three days in one cycle.", (("we", 22, 0x80),)),
    Piece("chest_game", "Clock Town", "Treasure Chest Shop",
          "Win the Treasure Chest game as Goron Link.", (("chest", 0x17, 1),)),
    Piece("postbox", "Clock Town", "Postbox",
          "Check any postbox while wearing the Postman's Hat.", (("we", 81, 0x08),)),
    Piece("keaton", "Clock Town", "Keaton Quiz",
          "Wear the Keaton Mask, slash the moving bush, and answer all five questions.",
          (("we", 79, 0x80),)),
    Piece("deku_playground", "Clock Town", "Deku Scrub Playground",
          "Win the North Clock Town playground on all three days.", (("we", 14, 0x80),)),
    Piece("nct_tree", "Clock Town", "North Clock Town Tree",
          "Sitting on top of the big tree in North Clock Town.", (("coll", 0x6E, 10),)),
    Piece("sct_platform", "Clock Town", "South Clock Town Ledge",
          "On a high ledge in South Clock Town, reached with a Deku Flower.",
          (("coll", 0x6F, 10),)),
    Piece("bank", "Clock Town", "Bank Reward",
          "Get your bank balance to 5,000 rupees (in MM3D the bank is in South Clock Town).",
          (("we", 59, 0x08),)),
    Piece("postman_game", "Clock Town", "Postman's Counting Game",
          "Stop his timer at exactly 10 seconds (the Bunny Hood helps).", (("we", 77, 0x01),)),
    Piece("rosa", "Clock Town", "Rosa Sisters",
          "Wear Kamaro's Mask and dance for the sisters in West Clock Town at night.",
          (("we", 75, 0x80),)),
    Piece("swordsman", "Clock Town", "Swordsman's School",
          "Get a perfect score on the expert course.", (("we", 63, 0x20),)),
    Piece("toilet_hand", "Clock Town", "Stock Pot Inn Toilet Hand",
          "Give the hand in the inn's toilet a piece of paper at midnight.",
          (("we", 90, 0x80),), inferable=True),
    Piece("grandma_short", "Clock Town", "Grandma: Short Story",
          "Wear the All-Night Mask, listen to her short story, and answer correctly.",
          (("we", 50, 0x02),)),
    Piece("grandma_long", "Clock Town", "Grandma: Long Story",
          "Wear the All-Night Mask, listen to her long story, and answer correctly.",
          (("we", 50, 0x04),)),
    # ---- Termina Field & Romani Ranch ------------------------------------
    Piece("gossip_grotto", "Termina Field & Ranch", "Gossip Stone Grotto",
          "Use one form's song to light all the stones in the grotto the same color.",
          (("we", 90, 0x10),)),
    Piece("tf_scrub", "Termina Field & Ranch", "Business Scrub (Grotto)",
          "Buy it from the Deku Scrub in a Termina Field grotto.", (("we", 53, 0x02),)),
    Piece("bio_baba", "Termina Field & Ranch", "Bio Deku Baba Grotto",
          "Bomb the rock to open the grotto, then defeat the underwater Bio Babas.",
          (("coll", 0x07, 2),)),
    Piece("tf_chest_a", "Termina Field & Ranch", "Grotto Chest (Peahat / Dodongo) #1",
          "Defeat the giant Peahat or the two Dodongos in their grottos, then open the chest.",
          (("coll", 0x07, 10),)),
    Piece("tf_chest_b", "Termina Field & Ranch", "Grotto Chest (Peahat / Dodongo) #2",
          "Whichever of the Peahat or Dodongo grotto chests you haven't opened yet.",
          (("coll", 0x07, 11),)),
    Piece("dog_race", "Termina Field & Ranch", "Doggy Racetrack",
          "Wear the Mask of Truth to pick the winning dog, then win big.",
          (("we", 8, 0x20),)),
    # ---- Southern Swamp & Woodfall ----------------------------------------
    Piece("swamp_gallery", "Southern Swamp & Woodfall", "Swamp Shooting Gallery",
          "Get a perfect score at the Road to Southern Swamp gallery.", (("we", 32, 0x02),)),
    Piece("rss_tree", "Southern Swamp & Woodfall", "Road to Swamp Tree",
          "Up in a tree along the Road to Southern Swamp.", (("coll", 0x40, 1),)),
    Piece("swamp_scrub", "Southern Swamp & Woodfall", "Tourist Center Roof (Scrub)",
          "Give the Land Title Deed to the swamp's Business Scrub, then fly to the roof.",
          (("coll", 0x45, 30), ("coll", 0x00, 30))),
    Piece("photo_contest", "Southern Swamp & Woodfall", "Pictograph Contest",
          "Take the best kind of pictograph to the Tourist Center guide.",
          (("we", 87, 0x04),)),
    Piece("deku_palace", "Southern Swamp & Woodfall", "Deku Palace Garden",
          "In Deku Palace's west garden, reached from the Deku Flowers.",
          (("coll", 0x2B, 30),)),
    Piece("woodfall_chest", "Southern Swamp & Woodfall", "Woodfall Platform Chest",
          "Chest on a platform in Woodfall, reached by Deku Flowers.",
          (("coll", 0x46, 10),)),
    # ---- Snowhead ----------------------------------------------------------
    Piece("frog_choir", "Snowhead", "Frog Choir",
          "Find all four frogs with Don Gero's Mask, then return to Mountain Village in spring.",
          (("we", 35, 0x80),)),
    Piece("goron_scrub", "Snowhead", "Goron Village Ledge (Scrub)",
          "Give the Swamp Title Deed to the Goron Village Business Scrub, then fly to the ledge.",
          (("coll", 0x4D, 30), ("coll", 0x48, 30))),
    Piece("snowhead_path", "Snowhead", "Path to Snowhead Pillar",
          "On top of a pillar along the Path to Snowhead.", (("coll", 0x5B, 8),)),
    Piece("twin_islands", "Snowhead", "Twin Islands Underwater Chest",
          "Dive as Zora to the chest at the bottom of the Twin Islands lake.",
          (("coll", 0x5D, 7), ("coll", 0x5E, 7))),
    # ---- Great Bay ---------------------------------------------------------
    Piece("fisherman", "Great Bay", "Fisherman's Jumping Game",
          "Beat the torch-jumping game on the Great Bay Coast island.", (("we", 82, 0x10),)),
    Piece("lab_fish", "Great Bay", "Marine Research Lab Fish",
          "Keep feeding the lab's fish until one big fish eats the others.",
          (("we", 56, 0x02),)),
    Piece("gbc_ledge", "Great Bay", "Great Bay Coast Ledge",
          "On a high ledge at Great Bay Coast (Hookshot).", (("coll", 0x37, 5),)),
    Piece("ocean_spider_house", "Great Bay", "Oceanside Spider House",
          "Shoot the colored masks in the order shown, then open the chest.",
          (("coll", 0x28, 31),)),
    Piece("beaver_race", "Great Bay", "Beaver Race (second prize)",
          "Beat the Beaver Bros' race a second time.", (("we", 25, 0x01),)),
    Piece("zora_cape", "Great Bay", "Zora Cape Like Like",
          "Defeat the underwater Like Like at Zora Cape.", (("coll", 0x38, 7),)),
    Piece("evan", "Great Bay", "Evan's Composition",
          "Learn the song in Mikau's diary and play it for Evan in Zora Hall.", (("we", 39, 0x20),)),
    Piece("zora_scrub", "Great Bay", "Zora Hall Ledge (Scrub)",
          "Give the Mountain Title Deed to the Zora Hall Business Scrub, then fly up.",
          (("coll", 0x4C, 30),)),
    Piece("seahorse", "Great Bay", "Pinnacle Rock Seahorses",
          "Bring the seahorse to Pinnacle Rock and reunite the pair.", (("we", 32, 0x01),)),
    Piece("pirate_sewer", "Great Bay", "Pirates' Fortress Sewer",
          "Inside a cage in the fortress sewers.", (("coll", 0x23, 12),)),
    # ---- Ikana -------------------------------------------------------------
    Piece("spirit_house", "Ikana", "Spirit House (Poe Sisters)",
          "Beat the Poe Sisters in the Ikana Canyon Spirit House.", (("we", 54, 0x40),)),
    Piece("ikana_scrub", "Ikana", "Ikana Canyon Ledge (Scrub)",
          "Give the Ocean Title Deed to the Ikana Business Scrub, then fly to the ledge.",
          (("coll", 0x13, 30),)),
    Piece("graveyard_ik", "Ikana", "Beneath the Graveyard (Iron Knuckle)",
          "On night 2 beneath Ikana Graveyard, defeat the Iron Knuckle and open the chest.",
          (("coll", 0x0C, 31),)),
    Piece("dampe", "Ikana", "Dampé's Digging",
          "Help Dampé dig up the Big Poe beneath the graveyard (in MM3D this gives a heart piece).",
          (("coll", 0x30, 31),)),
    Piece("ikana_castle", "Ikana", "Ancient Castle of Ikana",
          "On top of a pillar in the castle courtyard, reached with a Deku Flower.",
          (("coll", 0x1D, 10),)),
    Piece("secret_shrine", "Ikana", "Secret Shrine",
          "Beat all four mini-bosses in the Secret Shrine and open the last chest.",
          (("coll", 0x60, 10),)),
    # ---- Moon --------------------------------------------------------------
    Piece("moon_deku", "The Moon", "Deku Trial",
          "Give a moon child 1 mask and finish the Deku trial.", (("coll", 0x2A, 1),)),
    Piece("moon_goron", "The Moon", "Goron Trial",
          "Give a moon child 2 masks and finish the Goron trial.", (("coll", 0x3F, 1),)),
    Piece("moon_zora", "The Moon", "Zora Trial",
          "Give a moon child 3 masks and finish the Zora trial.", (("coll", 0x47, 1),)),
    Piece("moon_link", "The Moon", "Link Trial",
          "Give a moon child 4 masks and finish the Link trial.", (("coll", 0x66, 1),)),
]

assert len(PIECES) == TOTAL_PIECES, len(PIECES)
assert set(STEPS) == {p.id for p in PIECES}, set(STEPS) ^ {p.id for p in PIECES}


class SaveError(ValueError):
    pass


@dataclass
class SlotResult:
    path: Path
    player_name: str
    crc_ok: bool
    heart_containers: int          # total hearts (incl. the starting 3)
    pieces_in_progress: int        # 0-3 towards the next heart
    boss_containers: list[str]
    expected_total: int            # pieces collected, worked out from hearts
    collected: dict[str, str] = field(default_factory=dict)  # id -> "yes" | "inferred"
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
    def detected(self) -> int:
        return sum(1 for v in self.collected.values() if v == "yes")

    @property
    def collected_count(self) -> int:
        return len(self.collected)

    @property
    def unexplained(self) -> int:
        """Pieces the hearts say you have that no flag accounts for."""
        return self.expected_total - self.collected_count


def _flag_set(data: bytes, flag: Flag) -> bool:
    kind, a, b = flag
    if kind == "we":
        return bool(data[OFF_WEEK_EVENT + a] & b)
    word = WORD_COLLECTIBLE if kind == "coll" else WORD_CHEST
    off = OFF_SCENE_FLAGS + a * SCENE_STRIDE + word * 4
    return bool(struct.unpack_from("<I", data, off)[0] >> b & 1)


def read_slot(path: str | Path) -> SlotResult:
    path = Path(path)
    data = path.read_bytes()
    if len(data) != SAVE_SIZE:
        raise SaveError(f"{path.name} is {len(data):,} bytes; an MM3D slot is {SAVE_SIZE:,}.")
    if data[:3] != MAGIC:
        raise SaveError(f"{path.name} isn't a Majora's Mask 3D save (no 'MJR' header).")

    stored = struct.unpack_from("<H", data, OFF_CRC)[0]
    scratch = bytearray(data)
    scratch[OFF_CRC:OFF_CRC + 2] = b"\0\0"
    crc_ok = crc16(scratch) == stored

    name = data[OFF_NAME:OFF_NAME + 16].decode("utf-16le", "replace").split("\0")[0].strip()
    hearts = struct.unpack_from("<h", data, OFF_HEART_CAP)[0] >> 4
    reg = struct.unpack_from("<I", data, OFF_COLLECT_REG)[0]
    in_progress = reg >> 28 & 0xF

    bosses = [boss for scene, boss in BOSS_ROOMS.items() if _flag_set(data, ("coll", scene, 31))]
    expected = max(0, (hearts - 3 - len(bosses)) * 4 + in_progress)

    result = SlotResult(path, name or "(no name)", crc_ok, hearts, in_progress, bosses, expected)
    for p in PIECES:
        if any(_flag_set(data, f) for f in p.flags):
            result.collected[p.id] = "yes"

    # Pieces whose flag is wiped on a cycle reset: if the heart total shows
    # pieces no flag accounts for, credit them to these.
    spare = result.unexplained
    for p in PIECES:
        if spare <= 0:
            break
        if p.inferable and p.id not in result.collected:
            result.collected[p.id] = "inferred"
            spare -= 1

    view = SaveView(data)
    for cat in CATEGORIES:
        rows = [(c, bool(c.test(view)), c.detail(view) if c.detail else "") for c in cat.checks]
        result.categories.append((cat, rows))
    return result


def find_slot_siblings(path: Path) -> list[Path]:
    """save0/1/2.bin next to the chosen file, in slot order."""
    out = []
    for i in range(3):
        p = path.with_name(f"save{i}.bin")
        if p.is_file() and p.stat().st_size == SAVE_SIZE:
            out.append(p)
    return out or [path]


def discover_saves() -> list[Path]:
    """Look for MM3D slots in common emulator and download locations."""
    home = Path.home()
    roots = [
        home / ".local/share/azahar-emu/sdmc",
        home / ".local/share/citra-emu/sdmc",
        home / ".local/share/lime3ds-emu/sdmc",
        home / ".local/share/Lime3DS/sdmc",
        *home.glob(".var/app/*/data/*/sdmc"),
    ]
    found: list[Path] = []
    for root in roots:
        if root.is_dir():
            found += root.glob("Nintendo 3DS/*/*/title/00040000/*/data/*/save[0-2].bin")
    for d in (home / "Downloads", home / "Documents"):
        if d.is_dir():
            found += d.glob("save[0-2].bin")
            found += d.glob("*/save[0-2].bin")
    good = []
    for p in found:
        try:
            if p.stat().st_size == SAVE_SIZE and p.read_bytes()[:3] == MAGIC:
                good.append(p)
        except OSError:
            pass
    return sorted(set(good), key=lambda p: p.stat().st_mtime, reverse=True)


if __name__ == "__main__":
    import sys

    for arg in sys.argv[1:]:
        r = read_slot(arg)
        print(f"{r.path.name}: {r.player_name}  hearts={r.heart_containers} "
              f"+{r.pieces_in_progress}/4  bosses={r.boss_containers}  crc={'ok' if r.crc_ok else 'BAD'}")
        print(f"  collected {r.collected_count}/{TOTAL_PIECES} "
              f"(flags {r.detected}, expected from hearts {r.expected_total}, unexplained {r.unexplained})")
        for p in PIECES:
            mark = {"yes": "x", "inferred": "~"}.get(r.collected.get(p.id, ""), " ")
            print(f"  [{mark}] {p.region:26s} {p.name}")
