"""Zelda 100% Tracker — standalone app for Windows and Android (Flet / Flutter).

Uses the same save parsers and guides as the Linux desktop app (core.py and games/, copied next to
this file when the app is built). Build: see .github/workflows/apps.yml.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import sys
import threading
import time
from pathlib import Path

import flet as ft

HERE = Path(__file__).resolve().parent
for cand in (HERE, HERE.parent):                    # packaged app / running from the repo
    if (cand / "core.py").is_file():
        sys.path.insert(0, str(cand))
        break

import games  # noqa: E402
from core import SaveError, SlotRef  # noqa: E402

try:
    from theme import PALETTES  # noqa: E402
except ImportError:  # theme.py imports nothing GTK-specific, but keep a fallback
    PALETTES = {"default": ("#14251c", "#0b140f", "#1a2d22", "#7fbf6a")}

GOLD, GOLD_LIGHT = "#d9b45e", "#f2d98e"
PARCHMENT, PARCHMENT_DIM, INK = "#efe5cb", "#b9ad8f", "#1a1408"
HEART = "#e0433d"
DATA = Path(os.getenv("FLET_APP_STORAGE_DATA") or Path.home() / ".zelda-tracker-app")
MEDALS = {
    "emblem-favorite-symbolic": ft.Icons.FAVORITE, "starred-symbolic": ft.Icons.STAR,
    "audio-x-generic-symbolic": ft.Icons.MUSIC_NOTE, "media-playback-start-symbolic": ft.Icons.MUSIC_NOTE,
    "view-grid-symbolic": ft.Icons.GRID_VIEW, "go-up-symbolic": ft.Icons.ARROW_UPWARD,
    "applications-science-symbolic": ft.Icons.SCIENCE, "security-high-symbolic": ft.Icons.SHIELD,
    "emoji-nature-symbolic": ft.Icons.BUG_REPORT, "weather-clear-night-symbolic": ft.Icons.NIGHTLIGHT,
    "mail-unread-symbolic": ft.Icons.MAIL, "avatar-default-symbolic": ft.Icons.PERSON,
    "camera-photo-symbolic": ft.Icons.PHOTO_CAMERA, "face-smile-symbolic": ft.Icons.FACE,
    "applications-games-symbolic": ft.Icons.EXTENSION, "mark-location-symbolic": ft.Icons.PLACE,
    "emblem-ok-symbolic": ft.Icons.CIRCLE_OUTLINED, "emblem-shared-symbolic": ft.Icons.AUTO_AWESOME,
    "accessories-dictionary-symbolic": ft.Icons.MENU_BOOK, "weather-few-clouds-symbolic": ft.Icons.WB_SUNNY,
}


def palette(gid: str | None):
    top, bottom, card, accent = PALETTES.get(gid or "default", PALETTES["default"])
    return {"top": top, "bottom": bottom, "card": card, "accent": accent}


def alpha(hex_color: str, a: float) -> str:
    return ft.Colors.with_opacity(a, hex_color)


class TrackerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.serif = "Georgia" if page.platform == ft.PagePlatform.WINDOWS else "serif"
        self.game = None
        self.slots: list[SlotRef] = []
        self.slot = 0
        self.result = None
        self.section = None
        self.sources: list[str] = []      # the files the user picked (for re-reading while playing)
        self.batch_dir: Path | None = None
        self.filter = self.get("filter", "all")
        self._stamp = 0.0

        page.title = "Zelda 100% Tracker"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.theme = ft.Theme(color_scheme_seed=GOLD)
        page.dark_theme = ft.Theme(color_scheme_seed=GOLD)
        self.picker = ft.FilePicker(on_result=self.on_picked)
        page.overlay.append(self.picker)
        page.on_route_change = self.on_route
        page.on_view_pop = self.on_pop
        threading.Thread(target=self.watch_loop, daemon=True).start()
        page.go("/")
        # developer hook for testing: ZT_OPEN="a.bin,b.bin" opens saves, ZT_ROUTE="/game/hearts" jumps to a page
        if os.getenv("ZT_OPEN"):
            self.open_paths(os.environ["ZT_OPEN"].split(","))
            if os.getenv("ZT_ROUTE"):
                page.go(os.environ["ZT_ROUTE"])

    # ---- storage ------------------------------------------------------------------------------
    def get(self, key, default=None):
        try:
            v = self.page.client_storage.get("zt." + key)
            return default if v is None else v
        except Exception:  # noqa: BLE001
            return default

    def put(self, key, value):
        try:
            self.page.client_storage.set("zt." + key, value)
        except Exception:  # noqa: BLE001
            pass

    def toast(self, text):
        self.page.open(ft.SnackBar(ft.Text(text, color=PARCHMENT), bgcolor=palette(self.game and self.game.id)["card"]))

    # ---- files --------------------------------------------------------------------------------
    def pick(self, _e=None):
        self.picker.pick_files(dialog_title="Open your save files", allow_multiple=True)

    def on_picked(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        paths = [f.path for f in e.files if f.path]
        if not paths:
            self.toast("This device didn't give the app access to the file.")
            return
        self.open_paths(paths)

    def open_paths(self, paths: list[str], want_slot: str | None = None):
        # copy the files side by side into the app's own folder, so slot siblings line up
        DATA.mkdir(parents=True, exist_ok=True)
        batch = DATA / "saves" / str(int(time.time() * 1000))
        batch.mkdir(parents=True, exist_ok=True)
        copies = []
        for p in paths:
            try:
                dst = batch / Path(p).name
                shutil.copy2(p, dst)
                copies.append(dst)
            except OSError as err:
                self.toast(f"Couldn't read {Path(p).name}: {err}")
        game = first = None
        for c in copies:
            game = games.identify(c)
            if game:
                first = c
                break
        if not game:
            self.toast("None of those files is a save from a supported game.")
            shutil.rmtree(batch, ignore_errors=True)
            return
        if self.batch_dir and self.batch_dir != batch:
            shutil.rmtree(self.batch_dir, ignore_errors=True)
        self.game, self.batch_dir, self.sources = game, batch, list(paths)
        self.slots = game.slots(first)
        keys = [f"{s.path.name}#{s.index}" for s in self.slots]
        self.slot = keys.index(want_slot) if want_slot in keys else next(
            (i for i, s in enumerate(self.slots) if s.path == first), 0)
        self._stamp = self.source_stamp()
        self.remember()
        if self.load_slot():
            self.page.go("/game")

    def source_stamp(self) -> float:
        try:
            return max(os.path.getmtime(p) for p in self.sources)
        except (OSError, ValueError):
            return 0.0

    def watch_loop(self):
        """Re-read the save when it changes (works where the app can see the real file: Windows)."""
        while True:
            time.sleep(3)
            if not self.sources or not self.result:
                continue
            stamp = self.source_stamp()
            if stamp and self._stamp and stamp > self._stamp:
                self._stamp = stamp
                try:
                    for p in self.sources:
                        shutil.copy2(p, self.batch_dir / Path(p).name)
                    if self.load_slot():
                        self.render()
                        self.toast("Save changed — updated")
                except OSError:
                    pass

    def remember(self):
        recents = [r for r in self.get("recent", []) if r.get("sources") != self.sources]
        recents.insert(0, {"game": self.game.id, "title": self.game.title, "short": self.game.short,
                           "sources": self.sources, "slot": self.slot_key(), "when": time.time()})
        self.put("recent", recents[:8])

    def slot_key(self) -> str:
        s = self.slots[self.slot]
        return f"{s.path.name}#{s.index}"

    def load_slot(self) -> bool:
        try:
            self.result = self.game.load(self.slots[self.slot])
        except (OSError, SaveError, IndexError, ValueError) as err:
            self.toast(f"Couldn't read the save: {err}")
            return False
        return True

    # ---- navigation ---------------------------------------------------------------------------
    def on_route(self, _e):
        route = self.page.route
        self.page.views.clear()
        self.page.views.append(self.home_view())
        if route.startswith("/game") and self.result:
            self.page.views.append(self.overview_view())
            if route.startswith("/game/"):
                self.section = route.split("/", 2)[2]
                self.page.views.append(self.section_view())
            else:
                self.section = None
        self.page.update()

    def on_pop(self, _e):
        self.page.views.pop()
        self.page.go(self.page.views[-1].route)

    def render(self):
        self.on_route(None)

    # ---- shared pieces ------------------------------------------------------------------------
    def colors(self):
        return palette(self.game.id if self.game else None)

    def bg(self, content, pal):
        return ft.Container(content=content, expand=True,
                            gradient=ft.RadialGradient(center=ft.Alignment(0, -1.2), radius=1.6,
                                                       colors=[pal["top"], pal["bottom"]]))

    def appbar(self, title, subtitle, pal, home=False, back=False):
        actions = [ft.IconButton(ft.Icons.FOLDER_OPEN, tooltip="Open save files", on_click=self.pick, icon_color=PARCHMENT)]
        if home:
            actions.append(ft.IconButton(ft.Icons.HOME, tooltip="Start page", icon_color=PARCHMENT,
                                         on_click=lambda e: self.page.go("/")))
        return ft.AppBar(
            title=ft.Column([ft.Text(title, font_family=self.serif, weight=ft.FontWeight.BOLD, color=GOLD_LIGHT, size=17),
                             ft.Text(subtitle, size=12, color=PARCHMENT_DIM)], spacing=0, tight=True,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            center_title=True, bgcolor=pal["top"], automatically_imply_leading=back,
            color=PARCHMENT, actions=actions, toolbar_height=60)

    def card(self, content, pal, padding=0):
        return ft.Container(content=content, bgcolor=alpha(pal["card"], 0.92), padding=padding,
                            border=ft.border.all(1, alpha(GOLD, 0.38)), border_radius=10,
                            shadow=ft.BoxShadow(blur_radius=10, color=alpha("#000000", 0.35), offset=ft.Offset(0, 3)))

    def heading(self, text, size=15):
        return ft.Text(text, font_family=self.serif, weight=ft.FontWeight.BOLD, color=GOLD_LIGHT, size=size)

    def chip(self, text, done=False):
        return ft.Container(ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=INK if done else GOLD_LIGHT),
                            bgcolor=GOLD if done else alpha("#000000", 0.25), border=ft.border.all(1, alpha(GOLD, 0.5)),
                            border_radius=99, padding=ft.padding.symmetric(2, 10))

    def bar(self, done, total, pal, height=8, width=None):
        frac = done / total if total else 0
        return ft.ProgressBar(value=frac, color=pal["accent"] if total and done == total else GOLD,
                              bgcolor=alpha("#000000", 0.45), bar_height=height, width=width, border_radius=99)

    def seal(self, status):
        if status == "yes":
            return ft.Container(ft.Icon(ft.Icons.CHECK, size=17, color="#2a1e08"), width=30, height=30, border_radius=99,
                                gradient=ft.RadialGradient(colors=[GOLD_LIGHT, GOLD]), alignment=ft.alignment.center,
                                tooltip="Done")
        if status == "inferred":
            return ft.Container(ft.Icon(ft.Icons.CHECK, size=17, color="#f6cf6a"), width=30, height=30, border_radius=99,
                                bgcolor=alpha("#e0a040", 0.28), border=ft.border.all(1, alpha("#f6cf6a", 0.8)),
                                alignment=ft.alignment.center, tooltip="Probably done (worked out from your other progress)")
        return ft.Container(width=30, height=30, border_radius=99, bgcolor=alpha("#000000", 0.35),
                            border=ft.border.all(1, alpha(GOLD, 0.35)), tooltip="Not done yet")

    def hearts_row(self, full, quarters, per):
        icons = [ft.Icon(ft.Icons.FAVORITE, color=HEART, size=22) for _ in range(full)]
        if quarters:
            icons.append(ft.Stack([ft.Icon(ft.Icons.FAVORITE, color=alpha("#000000", 0.6), size=22),
                                   ft.Container(ft.Icon(ft.Icons.FAVORITE, color=HEART, size=22),
                                                width=22 * quarters / per, clip_behavior=ft.ClipBehavior.HARD_EDGE)]))
        return ft.Row(icons, wrap=True, spacing=3, run_spacing=3, width=260)

    def ornament(self, pal):
        return ft.Row([ft.Container(height=1, expand=True, bgcolor=alpha(GOLD, 0.7)),
                       ft.Container(width=11, height=11, bgcolor=pal["accent"], rotate=ft.Rotate(math.pi / 4),
                                    border=ft.border.all(1, GOLD)),
                       ft.Container(height=1, expand=True, bgcolor=alpha(GOLD, 0.7))], spacing=8)

    def page_column(self, controls):
        # a centred column, at most 680 px wide, like the desktop app
        body = ft.Container(ft.Column(controls, spacing=14), padding=16, width=680)
        return ft.ListView(controls=[ft.Row([body], alignment=ft.MainAxisAlignment.CENTER)], expand=True, padding=0)

    # ---- start page ---------------------------------------------------------------------------
    def home_view(self):
        pal = palette(None)
        recents = [r for r in self.get("recent", []) if all(os.path.exists(p) for p in r.get("sources", []))]
        buttons = []
        if recents:
            r0 = recents[0]
            buttons.append(ft.FilledButton(f"Continue {r0['short']}", style=ft.ButtonStyle(bgcolor=GOLD, color=INK),
                                           on_click=lambda e, r=r0: self.open_paths(r["sources"], r.get("slot"))))
        buttons.append(ft.OutlinedButton("Open Save Files…", on_click=self.pick,
                                         style=ft.ButtonStyle(color=GOLD_LIGHT, side=ft.BorderSide(1, GOLD))))
        controls = [
            ft.Container(height=8),
            ft.Row([ft.Icon(ft.Icons.DIAMOND, color="#56c46a", size=26), ft.Icon(ft.Icons.FAVORITE, color=HEART, size=44),
                    ft.Icon(ft.Icons.DIAMOND, color="#5a8fe0", size=26)], alignment=ft.MainAxisAlignment.CENTER, spacing=24),
            ft.Text("Begin Your Quest", font_family=self.serif, size=28, weight=ft.FontWeight.BOLD, color=GOLD_LIGHT,
                    text_align=ft.TextAlign.CENTER),
            ft.Container(self.ornament(pal), padding=ft.padding.symmetric(0, 60)),
            ft.Text("Pick up where you left off, or open any save. Select all slot files at once "
                    "(save00–save04) to get a tab for each.", color=PARCHMENT_DIM, text_align=ft.TextAlign.CENTER),
            ft.Row(buttons, alignment=ft.MainAxisAlignment.CENTER, wrap=True),
        ]
        if recents:
            tiles = []
            for i, r in enumerate(recents):
                tiles.append(ft.ListTile(
                    leading=self.badge(r["game"], r["short"]), title=ft.Text(r["title"], color=PARCHMENT),
                    subtitle=ft.Text(", ".join(Path(p).name for p in r["sources"]), color=PARCHMENT_DIM, size=12),
                    trailing=self.chip("Last played") if i == 0 else ft.Icon(ft.Icons.CHEVRON_RIGHT, color=PARCHMENT_DIM),
                    on_click=lambda e, r=r: self.open_paths(r["sources"], r.get("slot"))))
            controls += [self.heading("Recent Saves"), self.card(ft.Column(tiles, spacing=0), pal)]
        controls.append(self.heading("Supported Games"))
        controls.append(ft.ResponsiveRow([
            ft.Row([self.badge(g.id, g.short), ft.Column([ft.Text(g.title, font_family=self.serif, weight=ft.FontWeight.BOLD,
                                                                  color=PARCHMENT),
                                                          ft.Text(g.platform, size=12, color=PARCHMENT_DIM)], spacing=0, expand=True)],
                   col={"xs": 12, "sm": 6}) for g in games.GAMES], run_spacing=10))
        controls.append(ft.Text("Where to find saves: 3DS slot files from Checkpoint/JKSM or Azahar/Citra (save00.bin…), "
                                "Game Boy/GBA/SNES .sav or .srm files from your emulator, GameCube .gci exports from Dolphin.",
                                size=12, color=PARCHMENT_DIM))
        return ft.View("/", [self.bg(self.page_column(controls), pal)], padding=0, bgcolor=pal["bottom"],
                       appbar=self.appbar("Zelda 100% Tracker", "Choose a save to begin", pal))

    def badge(self, gid, short):
        acc = palette(gid)["accent"]
        return ft.Container(ft.Text(short, size=11, weight=ft.FontWeight.W_800, color="#14100a", font_family=self.serif),
                            width=64, height=30, alignment=ft.alignment.center, border_radius=8,
                            border=ft.border.all(1, alpha(GOLD, 0.6)), bgcolor=acc)

    # ---- overview -----------------------------------------------------------------------------
    def overview_view(self):
        r, pal = self.result, self.colors()
        done, total = r.overall
        pct = math.floor(100 * done / total) if total else 0
        plaque = [
            ft.Text(f"{r.game.platform.upper()} · QUEST LOG", size=11, weight=ft.FontWeight.BOLD, color=pal["accent"]),
            ft.Row([ft.Column([ft.Text(r.game.title, font_family=self.serif, size=20, weight=ft.FontWeight.BOLD, color=PARCHMENT),
                               ft.Text(" · ".join([r.player_name, *r.tags]), color=PARCHMENT_DIM)], expand=True, spacing=2),
                    ft.Text(spans=[ft.TextSpan(str(pct), ft.TextStyle(size=50, weight=ft.FontWeight.W_800, color=GOLD_LIGHT,
                                                                      font_family=self.serif)),
                                   ft.TextSpan("%", ft.TextStyle(size=22, color=GOLD, font_family=self.serif))])]),
            self.ornament(pal), self.bar(done, total, pal, 12),
            ft.Text(f"{done} of {total} checks complete", size=12.5, color=PARCHMENT_DIM),
        ]
        if r.hearts:
            plaque += [self.hearts_row(r.hearts, r.quarters, r.pieces_per_heart),
                       ft.Text(f"{r.hearts} hearts · {r.quarters}/{r.pieces_per_heart} toward the next", size=12.5,
                               color=PARCHMENT_DIM)]
        controls = []
        if len(self.slots) > 1:
            controls.append(self.slot_tabs(pal))
        controls.append(self.card(ft.Column(plaque, spacing=8), pal, padding=ft.padding.only(20, 16, 20, 18)))
        for b in r.banners:
            controls.append(self.card(ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE, color=GOLD_LIGHT), ft.Text(b, expand=True)]), pal, 12))
        tiles = []
        for s in r.sections:
            sd, st = s.done, len(s.rows)
            medal = ft.Container(ft.Icon(MEDALS.get(s.icon, ft.Icons.FAVORITE if s.icon is None else ft.Icons.DIAMOND),
                                         color="#2a1e08" if sd == st else (HEART if s.icon is None else pal["accent"]), size=20),
                                 width=40, height=40, border_radius=99, alignment=ft.alignment.center,
                                 gradient=ft.RadialGradient(colors=[GOLD_LIGHT, GOLD]) if sd == st else None,
                                 bgcolor=None if sd == st else alpha(pal["accent"], 0.2), border=ft.border.all(2, alpha(GOLD, 0.7)))
            tiles.append(ft.ListTile(leading=medal, title=ft.Text(s.title, color=PARCHMENT),
                                     subtitle=ft.Text(f"{sd} / {st}" + ("  ·  complete" if sd == st else ""), color=PARCHMENT_DIM, size=12),
                                     trailing=ft.Row([self.bar(sd, st, pal, 6, 80), ft.Icon(ft.Icons.CHEVRON_RIGHT, color=PARCHMENT_DIM)],
                                                     tight=True, spacing=6),
                                     on_click=lambda e, sid=s.id: self.page.go(f"/game/{sid}")))
        controls += [self.heading("Adventure Log"), self.card(ft.Column(tiles, spacing=0), pal)]
        if r.footnote:
            controls.append(ft.Text(r.footnote, size=12.5, color=PARCHMENT_DIM))
        return ft.View("/game", [self.bg(self.page_column(controls), pal)], padding=0, bgcolor=pal["bottom"],
                       appbar=self.appbar("Zelda 100% Tracker", f"{r.game.short} — {self.slots[self.slot].path.name}", pal,
                                          home=True))

    def slot_tabs(self, pal):
        def choose(i):
            self.slot = i
            if self.load_slot():
                self.remember()
                self.render()
        buttons = []
        for i, s in enumerate(self.slots):
            try:
                name = self.game.read(s).player_name
            except Exception:  # noqa: BLE001
                name = "?"
            on = i == self.slot
            buttons.append(ft.Container(ft.Text(f"{self.game.slot_label(s, i)} · {name}", weight=ft.FontWeight.BOLD,
                                                color=INK if on else PARCHMENT, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                                        bgcolor=GOLD if on else None, border_radius=99, expand=True, padding=8,
                                        alignment=ft.alignment.center, on_click=lambda e, i=i: choose(i)))
        return ft.Container(ft.Row(buttons, spacing=4), padding=4, border_radius=99, bgcolor=alpha("#000000", 0.35),
                            border=ft.border.all(1, alpha(GOLD, 0.3)))

    # ---- section pages ------------------------------------------------------------------------
    def tick_key(self):
        return f"ticks.{self.game.id}|{'+'.join(Path(p).name for p in self.sources)}|{self.slot_key()}"

    def section_view(self):
        r, pal = self.result, self.colors()
        sec = next((s for s in r.sections if s.id == self.section), None)
        if sec is None:
            return ft.View("/game/missing", [ft.Text("Section not found")])
        counted = sec.counted is not None
        all_done = counted and sec.counted >= len(sec.rows)
        ticks = set(self.get(self.tick_key(), []))

        def set_filter(f):
            self.filter = f
            self.put("filter", f)
            self.render()

        filt = ft.Row([ft.Container(ft.Text("All" if f == "all" else "Missing", weight=ft.FontWeight.BOLD,
                                            color=INK if self.filter == f else PARCHMENT),
                                    bgcolor=GOLD if self.filter == f else None, border_radius=8,
                                    padding=ft.padding.symmetric(5, 10), on_click=lambda e, f=f: set_filter(f))
                       for f in ("all", "missing")], spacing=2, tight=True)
        controls = [ft.Row([self.heading(sec.title, 20), ft.Container(filt, padding=3, border_radius=10,
                                                                     bgcolor=alpha("#000000", 0.35))],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN)]
        if sec.banner:
            controls.append(self.card(ft.Row([ft.Icon(ft.Icons.HELP_OUTLINE, color=GOLD_LIGHT), ft.Text(sec.banner, expand=True)]), pal, 12))
        intro = sec.intro + (" Tap a marker to tick off the ones you've found; the app remembers them."
                             if counted and not all_done else "")
        if intro.strip():
            controls.append(ft.Text(intro.strip(), color=PARCHMENT_DIM))
        if sec.guide:
            controls.append(self.card(ft.ExpansionTile(
                title=ft.Text("How to get these", color=PARCHMENT), subtitle=ft.Text("Step-by-step guide for this section", size=12, color=PARCHMENT_DIM),
                leading=ft.Icon(ft.Icons.INFO_OUTLINE, color=GOLD_LIGHT), controls=[self.steps(sec.guide)],
                collapsed_icon_color=PARCHMENT_DIM, icon_color=PARCHMENT_DIM), pal))
        groups: dict[str, list] = {}
        for row in sec.rows:
            groups.setdefault(row.group, []).append(row)
        shown = 0
        for title, members in groups.items():
            got = sum(1 for m in members if m.ok)
            show = [m for m in members if self.filter == "all" or
                    (not all_done and ((counted and m.id not in ticks) or (not counted and not m.ok)))]
            if not show:
                continue
            shown += len(show)
            if all_done:
                chip = self.chip(f"{len(members)} / {len(members)}", True)
            elif counted:
                mine = sum(1 for m in members if m.id in ticks)
                chip = self.chip(f"{mine} / {len(members)} ticked" if mine else str(len(members)))
            else:
                chip = self.chip(f"{got} / {len(members)}", got == len(members))
            items = [self.row(m, counted and not all_done, all_done, ticks) for m in show]
            controls += [ft.Row([self.heading(title or sec.title), chip], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                         self.card(ft.Column(items, spacing=0), pal)]
        if not shown:
            controls.append(ft.Column([self.heading("All done here!", 18), ft.Text("Nothing left to find in this section.",
                                                                                   color=PARCHMENT_DIM)],
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        return ft.View(f"/game/{sec.id}", [self.bg(self.page_column(controls), pal)], padding=0, bgcolor=pal["bottom"],
                       appbar=self.appbar(sec.title, r.game.short, pal, home=True, back=True))

    def steps(self, steps):
        lines = []
        for i, s in enumerate(steps, 1):
            lines.append(ft.Row([ft.Container(ft.Text(str(i), size=12, weight=ft.FontWeight.W_800, color=GOLD_LIGHT), width=22, height=22,
                                              border_radius=99, alignment=ft.alignment.center, bgcolor=alpha(GOLD, 0.2),
                                              border=ft.border.all(1, alpha(GOLD, 0.55))),
                                 ft.Text(s, color=PARCHMENT, expand=True, selectable=True)],
                                vertical_alignment=ft.CrossAxisAlignment.START, spacing=12))
        return ft.Container(ft.Column(lines, spacing=8), padding=ft.padding.only(16, 4, 16, 16))

    def row(self, m, guide_only, force_done, ticks):
        status = "yes" if force_done else m.status
        if guide_only:
            on = m.id in ticks

            def toggle(_e, rid=m.id):
                t = set(self.get(self.tick_key(), []))
                t.symmetric_difference_update({rid})
                self.put(self.tick_key(), sorted(t))
                self.render()
            lead = ft.Container(self.seal("yes").content if on else ft.Icon(ft.Icons.PLACE, size=17, color=self.colors()["accent"]),
                                width=30, height=30, border_radius=99, alignment=ft.alignment.center, on_click=toggle,
                                gradient=ft.RadialGradient(colors=[GOLD_LIGHT, GOLD]) if on else None,
                                bgcolor=None if on else alpha(self.colors()["accent"], 0.15),
                                border=None if on else ft.border.all(1, alpha(self.colors()["accent"], 0.45)),
                                tooltip="Tap to untick" if on else "Tap to tick this off once you've found it")
            done = on
        else:
            lead = self.seal(status)
            done = bool(status)
        sub = "\n".join(x for x in (m.hint, m.detail if not status and m.detail else "") if x)
        title = ft.Text(m.name, color=alpha(PARCHMENT, 0.55) if done else PARCHMENT,
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH, decoration_color=alpha(GOLD, 0.45)) if done else None)
        subtitle = ft.Text(sub, size=12.5, color=PARCHMENT_DIM) if sub else None
        if m.steps:
            return ft.ExpansionTile(title=title, subtitle=subtitle, leading=lead, controls=[self.steps(m.steps)],
                                    collapsed_icon_color=PARCHMENT_DIM, icon_color=PARCHMENT_DIM, maintain_state=False)
        return ft.ListTile(leading=lead, title=title, subtitle=subtitle)


def main(page: ft.Page):
    TrackerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
