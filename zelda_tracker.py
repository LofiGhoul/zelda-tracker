#!/usr/bin/env python3
"""Zelda Handheld 100% Tracker — GTK4 / libadwaita front end for every supported game."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import games  # noqa: E402
from core import Result, Row, SaveError, Section, SlotRef  # noqa: E402
import theme  # noqa: E402

APP_ID = "io.github.zelda_tracker"
STATE_FILE = Path(GLib.get_user_config_dir()) / "zelda-tracker" / "state.json"

CSS = theme.css()


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state))
    except OSError:
        pass


class HeartMeter(Gtk.DrawingArea):
    """In-game style heart row: full hearts plus a quarter-filled one in progress."""

    SIZE, GAP, PER_ROW = 22, 4, 10

    def __init__(self, full: int, quarters: int, per: int = 4):
        super().__init__()
        self.full, self.quarters, self.per = full, quarters, per
        n = full + (1 if quarters else 0)
        self.set_content_width(min(max(n, 1), self.PER_ROW) * (self.SIZE + self.GAP))
        self.set_content_height(max(1, math.ceil(n / self.PER_ROW)) * (self.SIZE + self.GAP))
        self.set_draw_func(self._draw)

    def _draw(self, _area, cr, _w, _h):
        s, g = self.SIZE, self.GAP
        items = [1.0] * self.full + ([self.quarters / self.per] if self.quarters else [])
        for i, fill in enumerate(items):
            x = (i % self.PER_ROW) * (s + g) + 1
            y = (i // self.PER_ROW) * (s + g) + 1
            theme.draw_heart(cr, x, y, s - 2, fill)


def heart_icon() -> Gtk.Widget:
    area = Gtk.DrawingArea(content_width=20, content_height=20, margin_start=8, margin_end=8,
                           valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER)

    def draw(_a, cr, _w, _h):
        theme.draw_heart(cr, 1, 1, 18, 1.0)
    area.set_draw_func(draw)
    box = Gtk.Box(valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER, hexpand=False)
    box.add_css_class("cat-icon")
    box.append(area)
    return box


def status_icon(status: str | None, tip_inferred: str = "") -> Gtk.Widget:
    icon_name, cls, tip = {
        "yes": ("object-select-symbolic", "got", "Done"),
        "inferred": ("dialog-question-symbolic", "maybe", tip_inferred),
        None: ("radio-symbolic", "missing", "Not done yet"),
    }[status]
    img = Gtk.Image(icon_name=icon_name, valign=Gtk.Align.CENTER, tooltip_text=tip)
    img.add_css_class("piece-icon")
    img.add_css_class(cls)
    return img


def progress_bar(done: int, total: int, css: str) -> Gtk.ProgressBar:
    bar = Gtk.ProgressBar(fraction=done / total if total else 0, valign=Gtk.Align.CENTER)
    bar.add_css_class(css)
    if total and done == total:
        bar.add_css_class("done")
    return bar


def chip(text: str, done: bool) -> Gtk.Label:
    lbl = Gtk.Label(label=text, valign=Gtk.Align.CENTER)
    lbl.add_css_class("region-chip")
    if done:
        lbl.add_css_class("done")
    return lbl


def ornament(width: int = -1) -> Gtk.Widget:
    area = Gtk.DrawingArea(content_height=14, hexpand=width < 0, halign=Gtk.Align.FILL if width < 0 else Gtk.Align.CENTER)
    if width > 0:
        area.set_content_width(width)
    area.set_draw_func(lambda _a, cr, w, h: theme.draw_ornament(cr, w, h))
    return area


# Optional icons you supply yourself (none ship with the app). A file named after the
# check id without its prefix, e.g. "hookshot.png" for i_hookshot, "lullaby.png" for s_lullaby.
ICON_DIRS = (
    Path(__file__).resolve().parent / "icons",
    Path(GLib.get_user_data_dir()) / "zelda-tracker" / "icons",
)
ICON_EXTS = (".png", ".svg", ".webp", ".jpg", ".jpeg")
_icon_cache: dict[str, Path | None] = {}




def item_picture(path: Path, owned: bool, size: int) -> Gtk.Widget:
    pic = Gtk.Image.new_from_file(str(path))
    pic.set_pixel_size(size)
    pic.set_valign(Gtk.Align.CENTER)
    if not owned:
        pic.add_css_class("not-owned")
    return pic

def find_game_icon(game_id: str, row_id: str) -> Path | None:
    """icons/<game>/<id without prefix>.png, e.g. icons/oot3d/hookshot.png for i_hookshot."""
    key = f"{game_id}/{row_id}"
    if key not in _icon_cache:
        stem = row_id.split("_", 1)[-1]
        _icon_cache[key] = next(
            (d / game_id / f"{stem}{ext}" for d in ICON_DIRS for ext in ICON_EXTS
             if (d / game_id / f"{stem}{ext}").is_file()), None)
    return _icon_cache[key]


INFERRED_TIP = "Probably done: worked out from your heart total, since the save has no flag for it."


class TrackerWindow(Adw.ApplicationWindow):
    def __init__(self, app, initial: Path | None):
        super().__init__(application=app, title="Zelda 100% Tracker")
        self.set_default_size(560, 860)
        self.add_css_class("zelda")
        self.state = load_state()
        self.game: games.Game | None = None
        self.slots: list[SlotRef] = []
        self.current: SlotRef | None = None
        self.result: Result | None = None
        self.monitor: Gio.FileMonitor | None = None
        self._reload_id = 0
        self.filter_mode = self.state.get("filter", "all")
        self.detail_page: Adw.NavigationPage | None = None
        self.detail_sec: str | None = None
        self.detail_scroller: Gtk.ScrolledWindow | None = None

        self.toasts = Adw.ToastOverlay()
        self.nav = Adw.NavigationView()
        self.nav.connect("popped", self._on_popped)
        self.toasts.set_child(self.nav)
        self.set_content(self.toasts)

        view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        open_btn = Gtk.Button(icon_name="document-open-symbolic", tooltip_text="Open save file (Ctrl+O)")
        open_btn.connect("clicked", lambda *_: self.choose_file())
        header.pack_start(open_btn)
        self.reload_btn = Gtk.Button(icon_name="view-refresh-symbolic", tooltip_text="Reload (Ctrl+R)",
                                     sensitive=False)
        self.reload_btn.connect("clicked", lambda *_: self.reload())
        header.pack_start(self.reload_btn)
        self.home_btn = Gtk.Button(icon_name="go-home-symbolic", tooltip_text="Start page (Alt+Home)",
                                   sensitive=False)
        self.home_btn.connect("clicked", lambda *_: self.show_home())
        header.pack_end(self.home_btn)
        self.title = Adw.WindowTitle(title="Zelda 100% Tracker", subtitle="Choose a save to begin")
        header.set_title_widget(self.title)
        view.add_top_bar(header)

        self.slot_bar = Gtk.Box(margin_start=12, margin_end=12, margin_top=6, margin_bottom=6, visible=False)
        self.slot_group = Adw.ToggleGroup(hexpand=True)
        self.slot_group.add_css_class("round")
        self.slot_group.connect("notify::active-name", self._on_slot_toggled)
        self.slot_bar.append(self.slot_group)
        view.add_top_bar(self.slot_bar)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        self.welcome_scroller = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.stack.add_named(self.welcome_scroller, "empty")
        self.overview_scroller = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.stack.add_named(self.overview_scroller, "overview")
        view.set_content(self.stack)
        self.nav.add(Adw.NavigationPage(child=view, title="Overview", tag="overview"))

        drop = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop.connect("drop", self._on_drop)
        self.add_controller(drop)
        ctl = Gtk.ShortcutController()
        for accel, cb in (("<Control>o", self.choose_file), ("<Control>r", self.reload),
                          ("<Alt>Home", self.show_home)):
            ctl.add_shortcut(Gtk.Shortcut(trigger=Gtk.ShortcutTrigger.parse_string(accel),
                                          action=Gtk.CallbackAction.new(lambda *_a, f=cb: (f(), True)[1])))
        self.add_controller(ctl)

        if initial:
            self.open_path(initial)
        else:
            self.show_home()

    # ---- file handling ------------------------------------------------------
    def choose_file(self):
        dlg = Gtk.FileDialog(title="Open a Zelda save")
        f = Gtk.FileFilter(name="Save files")
        for ext in sorted(games.SAVE_EXTS):
            f.add_suffix(ext.lstrip("."))
        every = Gtk.FileFilter(name="All files")
        every.add_pattern("*")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(f)
        filters.append(every)
        dlg.set_filters(filters)
        if self.current:
            dlg.set_initial_folder(Gio.File.new_for_path(str(self.current.path.parent)))
        dlg.open(self, None, self._on_file_chosen)

    def _on_file_chosen(self, dlg, res):
        try:
            gfile = dlg.open_finish(res)
        except GLib.Error:
            return
        if gfile and gfile.get_path():
            self.open_path(Path(gfile.get_path()))

    def _on_drop(self, _target, value, _x, _y):
        files = value.get_files()
        if files and files[0].get_path():
            self.open_path(Path(files[0].get_path()))
            return True
        return False

    def open_path(self, path: Path, want_slot: str | None = None):
        game = games.identify(path)
        if game is None:
            self.toasts.add_toast(Adw.Toast(
                title=f"{path.name} isn't a save from a supported game.", timeout=6))
            return
        try:
            slots = game.slots(path)
        except (OSError, SaveError) as e:
            self.toasts.add_toast(Adw.Toast(title=str(e), timeout=6))
            return
        if not slots:
            self.toasts.add_toast(Adw.Toast(title=f"{path.name} has no saved games yet.", timeout=6))
            return
        self.game, self.slots = game, slots
        recent = [p for p in self.state.get("recent", []) if p != str(path)]
        self.state["recent"] = [str(path)] + recent[:7]
        save_state(self.state)
        self.home_btn.set_sensitive(True)
        self.slot_group.remove_all()
        for i, s in enumerate(slots):
            try:
                label = game.read(s).player_name
            except (OSError, SaveError, IndexError, ValueError):
                label = "?"
            self.slot_group.add(Adw.Toggle(name=s.key, label=f"{game.slot_label(s, i)} · {label}",
                                           tooltip=str(s.path)))
        self.slot_bar.set_visible(len(slots) > 1)
        pick = next((s for s in slots if s.key == want_slot), None)
        pick = pick or next((s for s in slots if s.path == path), slots[0])
        self.current = pick
        self.slot_group.set_active_name(pick.key)
        self.show_slot(pick)

    def _on_slot_toggled(self, group, _pspec):
        name = group.get_active_name()
        if name and (self.current is None or name != self.current.key):
            slot = next((s for s in self.slots if s.key == name), None)
            if slot:
                self.show_slot(slot)

    def show_slot(self, slot: SlotRef):
        changed_file = self.current is None or self.monitor is None or slot.path != self.current.path
        self.current = slot
        self.state["last"] = str(slot.path)
        self.state["last_slot"] = slot.key
        save_state(self.state)
        if changed_file or self.monitor is None:
            if self.monitor:
                self.monitor.cancel()
            self.monitor = Gio.File.new_for_path(str(slot.path)).monitor_file(Gio.FileMonitorFlags.NONE, None)
            self.monitor.connect("changed", self._on_file_changed)
        if self.detail_page:
            self.nav.pop_to_tag("overview")
        self.reload(quiet=True)

    def _on_file_changed(self, *_):
        if self._reload_id:
            GLib.source_remove(self._reload_id)
        self._reload_id = GLib.timeout_add(400, self._delayed_reload)

    def _delayed_reload(self):
        self._reload_id = 0
        self.reload(auto=True)
        return GLib.SOURCE_REMOVE

    def reload(self, quiet: bool = False, auto: bool = False):
        if not self.current or not self.game:
            return
        try:
            self.result = self.game.load(self.current)
        except (OSError, SaveError, IndexError, ValueError) as e:
            self.toasts.add_toast(Adw.Toast(title=f"Couldn't read save: {e}", timeout=6))
            return
        self._set_scrolled(self.overview_scroller, self._build_overview(self.result), keep=auto)
        if self.detail_sec and self.detail_scroller:
            self._set_scrolled(self.detail_scroller, self._build_detail(self.detail_sec), keep=True)
        self.stack.set_visible_child_name("overview")
        self.reload_btn.set_sensitive(True)
        r = self.result
        for cls in list(self.get_css_classes()):
            if cls.startswith("game-"):
                self.remove_css_class(cls)
        self.add_css_class(f"game-{r.game.id}")
        self.title.set_title("Zelda 100% Tracker")
        self.title.set_subtitle(f"{r.game.short} — {self.current.path.name}")
        if not quiet:
            self.toasts.add_toast(Adw.Toast(title="Save changed — updated" if auto else "Reloaded", timeout=2))

    @staticmethod
    def _set_scrolled(scroller: Gtk.ScrolledWindow, child: Gtk.Widget, keep: bool):
        pos = scroller.get_vadjustment().get_value() if keep else 0.0
        scroller.set_child(Gtk.Viewport(scroll_to_focus=False, child=child))

        def restore():
            scroller.get_vadjustment().set_value(pos)
            return GLib.SOURCE_REMOVE
        GLib.idle_add(restore)

    # ---- overview -------------------------------------------------------------
    def _build_overview(self, r: Result) -> Gtk.Widget:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18,
                       margin_top=18, margin_bottom=30, margin_start=12, margin_end=12)
        page.append(self._summary_card(r))
        for text in r.banners:
            page.append(self._banner("dialog-warning-symbolic", text))
        group = Adw.PreferencesGroup(title="Adventure Log")
        for sec in r.sections:
            group.add(self._section_row(sec))
        page.append(group)
        if r.footnote:
            note = Gtk.Label(label=r.footnote, wrap=True, xalign=0)
            note.add_css_class("caption")
            note.add_css_class("dim-label")
            page.append(note)
        return Adw.Clamp(maximum_size=640, child=page)

    def _summary_card(self, r: Result) -> Gtk.Widget:
        done, total = r.overall
        pct = math.floor(100 * done / total) if total else 0
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        card.add_css_class("card")
        card.add_css_class("z-plaque")
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                        margin_top=16, margin_bottom=18, margin_start=20, margin_end=20)
        card.append(inner)

        kicker = Gtk.Label(label=f"{r.game.platform.upper()} · QUEST LOG", xalign=0)
        kicker.add_css_class("z-kicker")
        inner.append(kicker)
        top = Gtk.Box(spacing=14)
        names = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER, hexpand=True)
        title = Gtk.Label(label=r.game.title, xalign=0, wrap=True)
        title.add_css_class("z-game-title")
        hero = Gtk.Label(label=f"{r.player_name}" + "".join(f" · {t}" for t in r.tags), xalign=0)
        hero.add_css_class("dim-label")
        names.append(title)
        names.append(hero)
        top.append(names)
        nums = Gtk.Box(spacing=2, valign=Gtk.Align.CENTER)
        big = Gtk.Label(label=str(pct))
        big.add_css_class("hero-count")
        sign = Gtk.Label(label="%", valign=Gtk.Align.BASELINE)
        sign.add_css_class("hero-total")
        nums.append(big)
        nums.append(sign)
        top.append(nums)
        inner.append(top)
        inner.append(ornament())
        bar = progress_bar(done, total, "big")
        inner.append(bar)
        sub = Gtk.Label(label=f"{done} of {total} checks complete", xalign=0)
        sub.add_css_class("caption")
        sub.add_css_class("dim-label")
        inner.append(sub)
        if r.hearts:
            inner.append(HeartMeter(r.hearts, r.quarters, r.pieces_per_heart))
            info = Gtk.Label(label=f"{r.hearts} hearts · {r.quarters}/{r.pieces_per_heart} toward the next",
                             xalign=0)
            info.add_css_class("caption")
            info.add_css_class("dim-label")
            inner.append(info)
        return card

    # ---- start page ---------------------------------------------------------------
    def show_home(self):
        if self.monitor:
            self.monitor.cancel()
            self.monitor = None
        if self.detail_page:
            self.nav.pop_to_tag("overview")
        self.current, self.game, self.result = None, None, None
        for cls in list(self.get_css_classes()):
            if cls.startswith("game-"):
                self.remove_css_class(cls)
        self.slot_bar.set_visible(False)
        self.reload_btn.set_sensitive(False)
        self.home_btn.set_sensitive(False)
        self.title.set_title("Zelda 100% Tracker")
        self.title.set_subtitle("Choose a save to begin")
        self._set_scrolled(self.welcome_scroller, self._welcome_page(), keep=False)
        self.stack.set_visible_child_name("empty")

    @staticmethod
    def _save_summary(game, path: Path) -> str:
        try:
            names = [game.read(sl).player_name for sl in game.slots(path)[:3]]
        except Exception:  # noqa: BLE001 — a broken save shouldn't break the start page
            names = []
        where = str(path.parent).replace(str(Path.home()), "~")
        return " · ".join(filter(None, [", ".join(names), path.name, where]))

    def _save_row(self, game, path: Path, last: bool = False) -> Gtk.Widget:
        row = Adw.ActionRow(title=GLib.markup_escape_text(game.title), activatable=True,
                            subtitle=GLib.markup_escape_text(self._save_summary(game, path)))
        row.set_subtitle_lines(2)
        badge = Gtk.Box(valign=Gtk.Align.CENTER, halign=Gtk.Align.CENTER, homogeneous=True)
        badge.add_css_class("z-badge")
        badge.add_css_class(f"game-{game.id}")
        badge.append(Gtk.Label(label=game.short))
        row.add_prefix(badge)
        if last:
            tag = Gtk.Label(label="Last played", valign=Gtk.Align.CENTER)
            tag.add_css_class("region-chip")
            row.add_suffix(tag)
        row.add_suffix(Gtk.Image(icon_name="go-next-symbolic"))
        row.connect("activated", lambda *_: self.open_path(path))
        return row

    def _welcome_page(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14,
                      margin_top=28, margin_bottom=28, margin_start=12, margin_end=12)
        art = Gtk.DrawingArea(content_width=180, content_height=64, halign=Gtk.Align.CENTER)

        def draw(_a, cr, w, h):
            size = 40
            theme.draw_gem(cr, w / 2 - 70, 14, 18, 34, "#56c46a")
            theme.draw_heart(cr, w / 2 - size / 2, 8, size, 1.0)
            theme.draw_gem(cr, w / 2 + 52, 14, 18, 34, "#5a8fe0")
        art.set_draw_func(draw)
        box.append(art)
        title = Gtk.Label(label="Begin Your Quest")
        title.add_css_class("title-1")
        title.add_css_class("z-heading")
        box.append(title)
        box.append(ornament(240))
        lead = Gtk.Label(label="Pick up where you left off, or open any save.\nThe tracker works out which game it's from.",
                         justify=Gtk.Justification.CENTER, wrap=True)
        lead.add_css_class("dim-label")
        box.append(lead)

        # recent saves first, then saves found on this computer
        recent = []
        for p in self.state.get("recent", []):
            path = Path(p)
            g = games.identify(path) if path.is_file() else None
            if g:
                recent.append((g, path))
        buttons = Gtk.Box(spacing=10, halign=Gtk.Align.CENTER, margin_top=4)
        if recent:
            g, path = recent[0]
            cont = Gtk.Button(halign=Gtk.Align.CENTER)
            cont.add_css_class("pill")
            cont.add_css_class("suggested-action")
            cont.set_child(Gtk.Label(label=f"Continue {g.short}"))
            cont.set_tooltip_text(str(path))
            cont.connect("clicked", lambda *_: self.open_path(path, self.state.get("last_slot")))
            buttons.append(cont)
        open_btn = Gtk.Button(label="Open Save File…")
        open_btn.add_css_class("pill")
        open_btn.add_css_class("suggested-action" if not recent else "z-secondary")
        open_btn.connect("clicked", lambda *_: self.choose_file())
        buttons.append(open_btn)
        box.append(buttons)

        if recent:
            group = Adw.PreferencesGroup(title="Recent Saves", margin_top=10)
            for i, (g, path) in enumerate(recent):
                group.add(self._save_row(g, path, last=i == 0))
            box.append(group)
        # one row per file set (save0/1/2.bin of the same game in one folder show as one)
        def key(g, p):
            return (g.id, str(p.parent)) if g.id in ("mm3d", "oot3d", "albw") else (g.id, str(p))
        keys = {key(g, p) for g, p in recent}
        uniq = []
        for g, p in games.discover():
            if key(g, p) not in keys:
                keys.add(key(g, p))
                uniq.append((g, p))
        if uniq:
            group = Adw.PreferencesGroup(title="Found on This Computer", margin_top=4)
            for g, p in uniq[:8]:
                group.add(self._save_row(g, p))
            box.append(group)

        heading = Gtk.Label(label="Supported Games", xalign=0, margin_top=10)
        heading.add_css_class("z-heading")
        box.append(heading)
        grid = Gtk.Grid(column_spacing=18, row_spacing=10, column_homogeneous=True)
        grid.add_css_class("z-game-list")
        for i, g in enumerate(games.GAMES):
            cell = Gtk.Box(spacing=10)
            badge = Gtk.Box(valign=Gtk.Align.CENTER, homogeneous=True)
            badge.add_css_class("z-badge")
            badge.add_css_class(f"game-{g.id}")
            badge.append(Gtk.Label(label=g.short))
            cell.append(badge)
            name = Gtk.Label(label=g.title, xalign=0, ellipsize=3)
            name.add_css_class("z-game-name")
            plat = Gtk.Label(label=g.platform, xalign=0)
            plat.add_css_class("caption")
            text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
            text.append(name)
            text.append(plat)
            cell.append(text)
            grid.attach(cell, i % 2, i // 2, 1, 1)
        box.append(grid)
        tip = Gtk.Label(label="Tip: drop a save file anywhere on this window to open it. "
                              "Use the home button to come back here.", wrap=True, xalign=0, margin_top=6)
        tip.add_css_class("caption")
        tip.add_css_class("dim-label")
        box.append(tip)
        return Adw.Clamp(maximum_size=560, child=box)

    def _section_row(self, sec: Section) -> Gtk.Widget:
        done, total = sec.done, len(sec.rows)
        row = Adw.ActionRow(title=GLib.markup_escape_text(sec.title), activatable=True,
                            subtitle=f"{done} / {total}" + ("  ·  complete" if done == total else ""))
        if sec.icon:
            img = Gtk.Image(icon_name=sec.icon, valign=Gtk.Align.CENTER)
            img.add_css_class("cat-icon")
            if done == total:
                img.add_css_class("done")
            row.add_prefix(img)
        else:
            row.add_prefix(heart_icon())
        bar = progress_bar(done, total, "thin")
        bar.set_size_request(90, -1)
        row.add_suffix(bar)
        row.add_suffix(Gtk.Image(icon_name="go-next-symbolic"))
        row.connect("activated", lambda *_: self.open_section(sec.id, sec.title))
        return row

    # ---- section pages --------------------------------------------------------
    def open_section(self, sec_id: str, title: str):
        view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        filt = Adw.ToggleGroup()
        filt.add(Adw.Toggle(name="all", label="All"))
        filt.add(Adw.Toggle(name="missing", label="Missing"))
        filt.set_active_name(self.filter_mode)
        filt.connect("notify::active-name", self._on_filter_toggled)
        header.pack_end(filt)
        view.add_top_bar(header)
        scroller = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        view.set_content(scroller)
        page = Adw.NavigationPage(child=view, title=title)
        self.detail_page, self.detail_sec, self.detail_scroller = page, sec_id, scroller
        self._set_scrolled(scroller, self._build_detail(sec_id), keep=False)
        self.nav.push(page)

    def _on_popped(self, _nav, page):
        if page is self.detail_page:
            self.detail_page = self.detail_sec = self.detail_scroller = None

    def _on_filter_toggled(self, group, _pspec):
        self.filter_mode = group.get_active_name() or "all"
        self.state["filter"] = self.filter_mode
        save_state(self.state)
        if self.detail_sec and self.detail_scroller:
            self._set_scrolled(self.detail_scroller, self._build_detail(self.detail_sec), keep=False)

    def _build_detail(self, sec_id: str) -> Gtk.Widget:
        r = self.result
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18,
                       margin_top=18, margin_bottom=30, margin_start=12, margin_end=12)
        clamp = Adw.Clamp(maximum_size=640, child=page)
        sec = next((s for s in r.sections if s.id == sec_id), None) if r else None
        if sec is None:
            return clamp
        if sec.banner:
            page.append(self._banner("dialog-question-symbolic", sec.banner))
        if sec.intro:
            info = Gtk.Label(label=sec.intro, xalign=0, wrap=True)
            info.add_css_class("dim-label")
            page.append(info)
        if sec.guide:
            page.append(self._guide_card(sec.guide))
        grid = self._icon_grid(r.game.id, sec.rows)
        if grid:
            page.append(grid)
        groups: dict[str, list[Row]] = {}
        for row in sec.rows:
            groups.setdefault(row.group, []).append(row)
        shown_total = 0
        counted = sec.counted is not None
        for title, members in groups.items():
            got = sum(1 for m in members if m.ok)
            shown = [m for m in members if counted or self.filter_mode == "all" or not m.ok]
            if not shown:
                continue
            shown_total += len(shown)
            group = Adw.PreferencesGroup(title=GLib.markup_escape_text(title or sec.title))
            if counted:
                group.set_header_suffix(chip(f"{len(members)}", False))
            else:
                group.set_header_suffix(chip(f"{got} / {len(members)}", got == len(members)))
            for m in shown:
                group.add(self._row_widget(r.game.id, m, guide_only=counted))
            page.append(group)
        if not shown_total:
            page.append(Adw.StatusPage(icon_name="starred-symbolic", title="All done here!",
                                       description="Nothing left to find in this section."))
        return clamp

    @staticmethod
    def _steps_box(steps) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8,
                      margin_top=12, margin_bottom=14, margin_start=16, margin_end=16)
        for i, text in enumerate(steps, 1):
            line = Gtk.Box(spacing=10)
            num = Gtk.Label(label=str(i), valign=Gtk.Align.START, width_chars=2)
            num.add_css_class("step-num")
            body = Gtk.Label(label=text, wrap=True, xalign=0, hexpand=True, selectable=True)
            body.set_wrap_mode(2)  # Pango.WrapMode.WORD_CHAR
            line.append(num)
            line.append(body)
            box.append(line)
        return box

    def _guide_card(self, steps) -> Gtk.Widget:
        group = Adw.PreferencesGroup()
        row = Adw.ExpanderRow(title="How to get these", subtitle="Step-by-step guide for this section")
        row.add_prefix(Gtk.Image(icon_name="help-about-symbolic", valign=Gtk.Align.CENTER))
        row.add_row(self._steps_box(steps))
        group.add(row)
        return group

    @staticmethod
    def _row_widget(game_id: str, m: Row, guide_only: bool = False) -> Gtk.Widget:
        sub = m.hint + (f"\n{m.detail}" if m.detail and not m.ok else "")
        if m.steps:
            row = Adw.ExpanderRow(title=GLib.markup_escape_text(m.name),
                                  subtitle=GLib.markup_escape_text(sub.strip()))
            row.set_subtitle_lines(2)
            row.add_row(TrackerWindow._steps_box(m.steps))
        else:
            row = Adw.ActionRow(title=GLib.markup_escape_text(m.name),
                                subtitle=GLib.markup_escape_text(sub.strip()))
            row.set_subtitle_lines(3)
        if guide_only:
            img = Gtk.Image(icon_name="find-location-symbolic", valign=Gtk.Align.CENTER,
                            tooltip_text="Your save only stores the total, so this can't be ticked off")
            img.add_css_class("piece-icon")
            img.add_css_class("guide")
            row.add_prefix(img)
        else:
            row.add_prefix(status_icon(m.status, INFERRED_TIP))
        icon = find_game_icon(game_id, m.id)
        if icon:
            row.add_prefix(item_picture(icon, m.ok, 36))
        if m.status == "yes":
            row.add_css_class("got-row")
        if m.status == "inferred":
            tag = Gtk.Label(label="Inferred", valign=Gtk.Align.CENTER, tooltip_text=INFERRED_TIP)
            tag.add_css_class("caption")
            tag.add_css_class("warning")
            row.add_suffix(tag)
        return row

    @staticmethod
    def _icon_grid(game_id: str, rows: list[Row]) -> Gtk.Widget | None:
        with_icons = [(m, find_game_icon(game_id, m.id)) for m in rows]
        if not any(p for _m, p in with_icons):
            return None
        grid = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, homogeneous=True,
                           min_children_per_line=4, max_children_per_line=8,
                           column_spacing=6, row_spacing=6)
        grid.add_css_class("card")
        for m, path in with_icons:
            cell = (item_picture(path, m.ok, 48) if path else
                    Gtk.Image(icon_name="image-missing-symbolic", pixel_size=24, opacity=0.3))
            cell.set_tooltip_text(f"{m.name} — {'got it' if m.ok else 'missing'}")
            cell.set_margin_top(8)
            cell.set_margin_bottom(8)
            grid.append(cell)
        return grid

    @staticmethod
    def _banner(icon: str, text: str) -> Gtk.Widget:
        box = Gtk.Box(spacing=10)
        box.add_css_class("card")
        box.append(Gtk.Image(icon_name=icon, margin_start=14, valign=Gtk.Align.CENTER))
        box.append(Gtk.Label(label=text, wrap=True, xalign=0, hexpand=True,
                             margin_top=10, margin_bottom=10, margin_end=14))
        return box


class TrackerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)

    def do_startup(self):
        Adw.Application.do_startup(self)
        custom = Path(__file__).resolve().parent / "icons"
        if (custom / "app.png").is_file():
            Gtk.IconTheme.get_for_display(Gdk.Display.get_default()).add_search_path(str(custom))
            Gtk.Window.set_default_icon_name("app")
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        provider = Gtk.CssProvider()
        provider.connect("parsing-error", lambda _p, sec, err: print("CSS:", sec.to_string(), err.message, file=sys.stderr))
        provider.load_from_string(CSS)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        TrackerWindow(self, None).present()

    def do_open(self, files, _n, _hint):
        path = Path(files[0].get_path()) if files and files[0].get_path() else None
        TrackerWindow(self, path).present()


def main():
    return TrackerApp().run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
