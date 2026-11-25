"""Every supported game, and save-file detection across them."""

from __future__ import annotations

import re
from pathlib import Path

from core import Game, Result, Row, SaveError, Section, SlotRef

from .albw import LinkBetweenWorlds
from .alttp import LinkToThePast
from .ladx import LinksAwakening
from .tp import TwilightPrincess
from .oracles import OracleOfAges, OracleOfSeasons
from .tmc import MinishCap
from .mm3d import mm3d_save as _mm
from .oot3d import oot3d_save as _oot


def _check_rows(categories) -> list[Section]:
    out = []
    for cat, rows in categories:
        out.append(Section(cat.id, cat.title, cat.icon, [
            Row(c.id, c.name, c.hint, "yes" if ok else None, detail, getattr(c, "group", ""))
            for c, ok, detail in rows
        ]))
    return out


class MajorasMask3D(Game):
    id, title, short, platform = "mm3d", "Majora's Mask 3D", "MM3D", "3DS"
    file_help = "save0.bin, save1.bin or save2.bin from Checkpoint/JKSM or a 3DS emulator"

    def detect(self, path, data):
        return len(data) == _mm.SAVE_SIZE and data[:3] == _mm.MAGIC

    def slots(self, path):
        return [SlotRef(p) for p in _mm.find_slot_siblings(path)]

    def slot_label(self, slot, i):
        return str(int(slot.path.stem[-1]) + 1) if slot.path.stem[-1:].isdigit() else str(i + 1)

    def read(self, slot):
        try:
            r = _mm.read_slot(slot.path)
        except _mm.SaveError as e:
            raise SaveError(str(e)) from e
        hearts = Section("hearts", "Pieces of Heart", None, [
            Row(f"hp_{p.id}", p.name, p.hint, r.collected.get(p.id), group=p.region, steps=p.steps)
            for p in _mm.PIECES
        ])
        boss = ", ".join(r.boss_containers) if r.boss_containers else "none yet"
        hearts.intro = (f"{r.collected_count} of {_mm.TOTAL_PIECES} pieces · boss containers: {boss}. "
                        "Tap a piece for step-by-step instructions.")
        if r.unexplained > 0:
            hearts.banner = (f"Your hearts show {r.unexplained} more piece(s) than the save's flags "
                             "account for. One of the pieces marked missing may already be yours.")
        res = Result(self, slot, r.player_name, r.heart_containers, r.pieces_in_progress)
        res.sections = [hearts] + _check_rows(r.categories)
        if not r.crc_ok:
            res.banners.append("This save's checksum doesn't match. It may be damaged or edited, "
                               "so the results could be wrong.")
        res.footnote = ("Not tracked: Bomber's Notebook entries and fishing. Stray fairy and Gold "
                        "Skulltula counts reset each cycle, so those sections track the rewards instead. "
                        "The Stock Pot Inn toilet hand's flag is wiped each cycle, so it's worked out "
                        "from your hearts (marked Inferred).")
        return res


def _oot_is_mq(data: bytes):
    base = _oot.find_base(data)
    return None if base < 0 else bool(data[base + _oot.OFF_MQ])


class OcarinaOfTime3D(Game):
    id, title, short, platform = "oot3d", "Ocarina of Time 3D", "OoT3D", "3DS"
    file_help = "a save slot file (save00.bin, save01.bin, ...) from Checkpoint/JKSM or a 3DS emulator"
    master_quest = False

    def detect(self, path, data):
        return _oot_is_mq(data) is self.master_quest

    def slots(self, path):
        return [SlotRef(p) for p in _oot.find_slot_siblings(path)
                if _oot_is_mq(p.read_bytes()) is self.master_quest] or [SlotRef(path)]

    def slot_label(self, slot, i):
        m = re.search(r"(\d+)\.bin$", slot.path.name)
        if not m:
            return str(i + 1)
        n = int(m.group(1))
        # OoT3D keeps the normal quest in save00-02 and Master Quest in save03-05
        return str(n - 3 + 1 if self.master_quest and n >= 3 else n + 1)

    def read(self, slot):
        try:
            r = _oot.read_slot(slot.path)
        except _oot.SaveError as e:
            raise SaveError(str(e)) from e
        hearts = Section("hearts", "Pieces of Heart", None, [
            Row(f"hp_{p.id}", p.name, p.hint, r.collected.get(p.id), group=p.region, steps=p.steps)
            for p in _oot.PIECES
        ])
        hearts.intro = (f"{r.collected_count} of {_oot.TOTAL_PIECES} pieces · "
                        f"{len(r.boss_containers)} of 8 boss Heart Containers. "
                        "Tap a piece for step-by-step instructions.")
        if r.unexplained > 0:
            hearts.banner = (f"Your hearts show {r.unexplained} more piece(s) than the save's flags "
                             "account for. One of the pieces marked missing may already be yours.")
        res = Result(self, slot, r.player_name, r.heart_containers, r.pieces_in_progress)
        res.sections = [hearts] + _check_rows(r.categories)
        for s in res.sections:
            if s.id == "gold_skulltulas" and s.rows:
                s.intro = (f"{s.done} of {len(s.rows)} found · {s.rows[0].detail} · "
                           "Most of them only come out at night.")
                for row in s.rows:
                    row.detail = ""
        if r.master_quest and not self.master_quest:
            res.tags.append("Master Quest")
        res.footnote = ("Not tracked: the trading sequences, masks, Big Poe captures, cows and "
                        "small keys. Their rewards that matter for 100% are covered above.")
        return res


class OcarinaOfTime3DMQ(OcarinaOfTime3D):
    id, title, short = "oot3dmq", "Ocarina of Time 3D: Master Quest", "OoT3D MQ"
    master_quest = True


# Detection order matters only where formats could overlap; these don't.
GAMES: list[Game] = [
    LinksAwakening(),
    OracleOfSeasons(),
    OracleOfAges(),
    MinishCap(),
    OcarinaOfTime3D(),
    OcarinaOfTime3DMQ(),
    MajorasMask3D(),
    LinkBetweenWorlds(),
    TwilightPrincess(),
    LinkToThePast(),      # last: its marker is only two bytes
]


def identify(path: Path) -> Game | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) > 1 << 20:      # no supported save is anywhere near 1 MB
        return None
    for g in GAMES:
        try:
            if g.detect(path, data):
                return g
        except Exception:  # noqa: BLE001 — a probe must never crash detection
            continue
    return None


SAVE_EXTS = {".bin", ".sav", ".srm", ".sa1", ".dsv", ".gci"}


def discover() -> list[tuple[Game, Path]]:
    """Look for saves of any supported game in emulator folders and Downloads/Documents."""
    home = Path.home()
    cands: list[Path] = []
    for root in (home / ".local/share/azahar-emu/sdmc", home / ".local/share/azaharplus-emu/sdmc",
                 home / ".local/share/citra-emu/sdmc", home / ".local/share/lime3ds-emu/sdmc"):
        if root.is_dir():
            cands += root.glob("Nintendo 3DS/*/*/title/00040000/*/data/*/*.bin")
    for root in (home / ".local/share/dolphin-emu/GC", home / ".var/app/org.DolphinEmu.dolphin-emu/data/dolphin-emu/GC"):
        if root.is_dir():
            cands += root.glob("*/Card */*.gci")
    for d in (home / ".config/retroarch/saves", home / ".local/share/mgba",
              home / "Downloads", home / "Documents"):
        if d.is_dir():
            cands += [p for p in d.glob("*") if p.suffix.lower() in SAVE_EXTS]
            cands += [p for p in d.glob("*/*") if p.suffix.lower() in SAVE_EXTS]
    found = []
    for p in set(cands):
        try:
            if p.is_file() and p.stat().st_size <= 1 << 20:
                g = identify(p)
                if g:
                    found.append((g, p))
        except OSError:
            pass
    return sorted(found, key=lambda gp: gp[1].stat().st_mtime, reverse=True)
