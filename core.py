"""Shared model for every game: a save slot read into sections of checklist rows."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path


class SaveError(ValueError):
    pass


@dataclass
class Row:
    id: str                       # unique across the game; the overall % counts each id once
    name: str
    hint: str = ""
    status: str | None = None     # "yes", "inferred" or None (missing)
    detail: str = ""              # extra line shown while missing
    group: str = ""               # sub-heading on the section page
    steps: tuple[str, ...] = ()   # step-by-step instructions (shown in an expander)

    @property
    def ok(self) -> bool:
        return self.status is not None


@dataclass
class Section:
    id: str
    title: str
    icon: str | None              # symbolic icon name; None draws a heart
    rows: list[Row]
    intro: str = ""               # line shown above the rows
    banner: str = ""              # highlighted notice (e.g. inferred pieces)
    guide: tuple[str, ...] = ()   # how-to steps for the whole section (counted items)
    counted: int | None = None    # set when the save only stores a total: rows are a guide list
                                  # and this many of them are done (which ones is unknown)

    @property
    def done(self) -> int:
        if self.counted is not None:
            return min(self.counted, len(self.rows))
        return sum(1 for r in self.rows if r.ok)


@dataclass
class Result:
    game: "Game"
    slot: "SlotRef"
    player_name: str
    hearts: int = 0               # full heart containers (0 hides the heart meter)
    quarters: int = 0             # pieces toward the next heart
    pieces_per_heart: int = 4
    sections: list[Section] = field(default_factory=list)
    banners: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)      # shown in the title (e.g. "Master Quest")
    footnote: str = ""

    @property
    def overall(self) -> tuple[int, int]:
        done, total = set(), set()
        extra_done = extra_total = 0
        for s in self.sections:
            if s.counted is not None:
                extra_done += s.done
                extra_total += len(s.rows)
                continue
            for r in s.rows:
                total.add(r.id)
                if r.ok:
                    done.add(r.id)
        return len(done) + extra_done, len(total) + extra_total


@dataclass(frozen=True)
class SlotRef:
    path: Path
    index: int | None = None      # slot inside the file, or None when one file = one slot

    @property
    def key(self) -> str:
        return f"{self.path}#{self.index}" if self.index is not None else str(self.path)


class Game:
    id = ""
    title = ""
    short = ""
    platform = ""
    file_help = ""                # how to get the save file, shown on the empty page

    def detect(self, path: Path, data: bytes) -> bool:
        raise NotImplementedError

    def slots(self, path: Path) -> list[SlotRef]:
        """Every readable slot for this save (inside the file, or sibling files)."""
        return [SlotRef(path)]

    def slot_label(self, slot: SlotRef, i: int) -> str:
        return str(i + 1)

    def read(self, slot: SlotRef) -> Result:
        raise NotImplementedError

    def load(self, slot: SlotRef) -> Result:
        """read() plus the step-by-step guide from games/guides/<id>.py, if there is one."""
        res = self.read(slot)
        try:
            guide = importlib.import_module(f"games.guides.{self.id}")
        except ModuleNotFoundError:
            return res
        steps = getattr(guide, "STEPS", {})
        sections = getattr(guide, "SECTIONS", {})
        for sec in res.sections:
            if not sec.guide and sec.id in sections:
                sec.guide = tuple(sections[sec.id])
            for row in sec.rows:
                if not row.steps and row.id in steps:
                    row.steps = tuple(steps[row.id])
        return res


def popcount(v: int) -> int:
    return bin(v).count("1")


def bcd(v: int) -> int:
    hi, lo = v >> 4, v & 0xF
    return hi * 10 + lo if hi < 10 and lo < 10 else v
