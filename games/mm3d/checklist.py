"""Everything besides Pieces of Heart that counts toward 100% in Majora's Mask 3D.

All offsets are file offsets into a saveN.bin slot (see mm3d_save.py). Struct
layout from Z3DR/mm3dr common_data.h (SaveData starts at file+0x8), checked
against real saves.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable

# PlayerData (file 0x120)
OFF_MAGIC_ACQUIRED = 0x146
OFF_MAGIC_UPGRADES = 0x147
OFF_DOUBLE_DEFENSE = 0x148
OFF_OWLS = 0x14C              # u16 bitfield
# EquipmentData (file 0x152)
OFF_SWORD_SHIELD = 0x17A      # u16: sword bits 0-3, shield bits 4-11
# InventoryData (file 0x17C)
OFF_ITEMS = 0x17C             # 24 x u8, slot index == item id when owned
OFF_MASKS = 0x194             # 24 x u8 item ids
OFF_BOTTLES = 0x1AC           # 7 x u8 (0xFF = no bottle)
OFF_UPGRADES = 0x1F4          # u32: quiver 0-2, bomb bag 3-5, wallet 12-13
OFF_COLLECT = 0x1F8           # u32: remains 0-3, songs 6-16, notebook 18
OFF_STRAY_FAIRIES = 0x210     # 4 x u8: Woodfall, Snowhead, Great Bay, Stone Tower
OFF_SKULLTULAS = 0x1210       # u32: ocean count 0-15, swamp count 16-31
OFF_WEEK_EVENT = 0x1250
OFF_SCENE_FLAGS = 0x250


class SaveView:
    def __init__(self, data: bytes):
        self.d = data

    def u8(self, off: int) -> int:
        return self.d[off]

    def u16(self, off: int) -> int:
        return struct.unpack_from("<H", self.d, off)[0]

    def u32(self, off: int) -> int:
        return struct.unpack_from("<I", self.d, off)[0]

    def has_item(self, item_id: int) -> bool:
        return self.d[OFF_ITEMS + item_id] == item_id

    def has_mask(self, item_id: int) -> bool:
        return item_id in self.d[OFF_MASKS:OFF_MASKS + 24]

    def collect(self, bit: int) -> bool:
        return bool(self.u32(OFF_COLLECT) >> bit & 1)

    def upgrade(self, shift: int, width: int = 3) -> int:
        return self.u32(OFF_UPGRADES) >> shift & ((1 << width) - 1)

    def bottles(self) -> int:
        return sum(1 for b in self.d[OFF_BOTTLES:OFF_BOTTLES + 7] if b != 0xFF)

    def sword(self) -> int:
        return self.u16(OFF_SWORD_SHIELD) & 0xF

    def shield(self) -> int:
        return self.u16(OFF_SWORD_SHIELD) >> 4 & 0xFF

    def week_event(self, byte: int, mask: int) -> bool:
        return bool(self.d[OFF_WEEK_EVENT + byte] & mask)

    def collectible(self, scene: int, bit: int) -> bool:
        return bool(self.u32(OFF_SCENE_FLAGS + scene * 0x20 + 16) >> bit & 1)

    def stray_fairies(self, temple: int) -> int:
        return self.d[OFF_STRAY_FAIRIES + temple]

    def skulltulas(self, house: str) -> int:
        v = self.u32(OFF_SKULLTULAS)
        return v >> 16 if house == "swamp" else v & 0xFFFF


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    hint: str
    test: Callable[[SaveView], bool]
    detail: Callable[[SaveView], str] | None = None   # live progress, e.g. "7/15 fairies"


@dataclass(frozen=True)
class Category:
    id: str
    title: str
    icon: str
    checks: tuple[Check, ...]


def _item(id_, name, item_id, hint):
    return Check(id_, name, hint, lambda s, i=item_id: s.has_item(i))


def _mask(id_, name, item_id, hint):
    return Check(id_, name, hint, lambda s, i=item_id: s.has_mask(i))


def _song(id_, name, bit, hint):
    return Check(id_, name, hint, lambda s, b=bit: s.collect(b))


MASKS = Category("masks", "Masks", "face-smile-symbolic", (
    _mask("m_deku", "Deku Mask", 0x32, "From the Happy Mask Salesman after you get your ocarina back and learn the Song of Healing."),
    _mask("m_goron", "Goron Mask", 0x33, "Play the Song of Healing for Darmani's ghost (follow him with the Lens of Truth to the Goron Graveyard)."),
    _mask("m_zora", "Zora Mask", 0x34, "Push Mikau to shore at Great Bay Coast and play the Song of Healing."),
    _mask("m_fierce", "Fierce Deity's Mask", 0x35, "On the Moon, give the moon children every non-transformation mask, then talk to the last child."),
    _mask("m_truth", "Mask of Truth", 0x36, "Collect all 30 Gold Skulltulas in the Swamp Spider House in one cycle."),
    _mask("m_kafei", "Kafei's Mask", 0x37, "Talk to Madame Aroma in the Mayor's Residence on Day 1 or 2."),
    _mask("m_allnight", "All-Night Mask", 0x38, "Stop Sakon robbing the Bomb Shop lady on Night 1, then buy it at the Curiosity Shop on the Final Night."),
    _mask("m_bunny", "Bunny Hood", 0x39, "Wear the Bremen Mask and march the chicks into adult Cuccos at Romani Ranch's Cucco Shack."),
    _mask("m_keaton", "Keaton Mask", 0x3A, "Meet Kafei's partner in the Curiosity Shop's back room on the Final Day."),
    _mask("m_garo", "Garo's Mask", 0x3B, "Beat the Gorman Brothers in the horse race at Gorman Track (on Epona)."),
    _mask("m_romani", "Romani's Mask", 0x3C, "Protect Romani Ranch from the aliens on Night 1, then escort Cremia's milk cart on Day 2."),
    _mask("m_troupe", "Troupe Leader's Mask", 0x3D, "Wearing Romani's Mask, perform for Gorman in the Milk Bar with the Deku, Goron and Zora forms."),
    _mask("m_postman", "Postman's Hat", 0x3E, "Give Kafei's Express Mail to Mama to the postman. On the Final Day he flees town and gives you his hat."),
    _mask("m_couple", "Couple's Mask", 0x3F, "Finish the Anju & Kafei quest so they reunite at dawn on the Final Day."),
    _mask("m_greatfairy", "Great Fairy's Mask", 0x40, "Bring the Clock Town stray fairy to the Great Fairy in North Clock Town as human Link."),
    _mask("m_gibdo", "Gibdo Mask", 0x41, "Heal Pamela's father with the Song of Healing in the Ikana Canyon music box house."),
    _mask("m_dongero", "Don Gero's Mask", 0x42, "Give a Rock Sirloin to the hungry Goron in Mountain Village."),
    _mask("m_kamaro", "Kamaro's Mask", 0x43, "Play the Song of Healing for Kamaro at midnight in north Termina Field."),
    _mask("m_captain", "Captain's Hat", 0x44, "Wake Captain Keeta in Ikana Graveyard with the Sonata of Awakening and beat him in the race."),
    _mask("m_stone", "Stone Mask", 0x45, "Use the Lens of Truth to find Shiro on the Road to Ikana and give him a Red Potion."),
    _mask("m_bremen", "Bremen Mask", 0x46, "Talk to Guru-Guru at the Laundry Pool on Night 1 or 2."),
    _mask("m_blast", "Blast Mask", 0x47, "Stop Sakon from robbing the Bomb Shop lady in North Clock Town on Night 1."),
    _mask("m_scents", "Mask of Scents", 0x48, "After returning the Deku Princess, win the Deku Butler's race."),
    _mask("m_giant", "Giant's Mask", 0x49, "Found in a chest in the inverted Stone Tower Temple. You need it for the Twinmold fight."),
))

SONGS = Category("songs", "Songs", "audio-x-generic-symbolic", (
    _song("s_time", "Song of Time", 12, "Learned when you get your ocarina back from Skull Kid on the first night."),
    _song("s_healing", "Song of Healing", 13, "Taught by the Happy Mask Salesman after you get your ocarina back."),
    _song("s_epona", "Epona's Song", 14, "From Romani at Romani Ranch (Day 1), after you clear the boulder with a Powder Keg."),
    _song("s_soaring", "Song of Soaring", 15, "Read the stone tablet in the Southern Swamp on the way to Woodfall (as Deku Link)."),
    _song("s_storms", "Song of Storms", 16, "Learn it from Flat's ghost in his tomb beneath Ikana Graveyard (the Captain's Hat gets the graves opened)."),
    _song("s_sonata", "Sonata of Awakening", 6, "Taught by the captured monkey in Deku Palace (reach him as Deku Link)."),
    _song("s_lullaby", "Goron Lullaby", 7, "Thaw out the Goron Elder for the intro, then play it for his crying son in the Goron Shrine (as Goron Link)."),
    _song("s_bossa", "New Wave Bossa Nova", 8, "Return all seven Zora Eggs to the Marine Research Lab tank."),
    _song("s_elegy", "Elegy of Emptiness", 9, "Defeat Igos du Ikana in the Ancient Castle of Ikana throne room."),
    _song("s_oath", "Oath to Order", 10, "Taught by the Giants after you beat your first boss."),
))

ITEMS = Category("items", "Items", "applications-games-symbolic", (
    _item("i_ocarina", "Ocarina of Time", 0x00, "Take it back from Skull Kid on top of the Clock Tower on the first night."),
    _item("i_bow", "Hero's Bow", 0x01, "Woodfall Temple (after the Dinolfos fight)."),
    _item("i_fire", "Fire Arrow", 0x02, "Snowhead Temple (after the Wizzrobe fight)."),
    _item("i_ice", "Ice Arrow", 0x03, "Great Bay Temple (after the Wart fight)."),
    _item("i_light", "Light Arrow", 0x04, "Stone Tower Temple (after the Garo Master fight)."),
    _item("i_bombs", "Bombs (Bomb Bag)", 0x06, "Buy a Bomb Bag at the Bomb Shop in West Clock Town."),
    _item("i_bombchu", "Bombchu", 0x07, "Buy them at the Bomb Shop (or find them in grotto chests)."),
    _item("i_sticks", "Deku Sticks", 0x08, "Break Deku Babas, or buy them in shops."),
    _item("i_nuts", "Deku Nuts", 0x09, "From Mad Scrubs or shops."),
    _item("i_beans", "Magic Beans", 0x0A, "Buy from the Bean Seller in the Deku Palace grotto."),
    _item("i_keg", "Powder Keg", 0x0C, "Pass the Powder Keg Goron's test in Goron Village (as Goron Link)."),
    _item("i_picto", "Pictograph Box", 0x0D, "From Koume after you heal her in the Woods of Mystery with a Red Potion."),
    _item("i_lens", "Lens of Truth", 0x0E, "In the Lone Peak Shrine near Goron Village."),
    _item("i_hookshot", "Hookshot", 0x0F, "Pirates' Fortress interior, after defeating the Gerudo guard."),
    _item("i_gfsword", "Great Fairy's Sword", 0x10, "Return all 15 Stone Tower stray fairies to the Ikana Canyon Great Fairy."),
    Check("i_notebook", "Bombers' Notebook", "Catch all five Bombers in Clock Town (as Deku Link), or let Jim give it to you.",
          lambda s: s.collect(18)),
))

BOTTLE_SOURCES = (
    "Kotake in the Southern Swamp Potion Shop / Woods of Mystery (Red Potion).",
    "Romani, for defending Romani Ranch from the aliens on Night 1 (Milk).",
    "Win the first Beaver Race at the Waterfall Rapids.",
    "Win Koume's boat archery after Woodfall is cleared (MM3D gives a bottle here).",
    "Win the Goron Race at the Goron Racetrack (Gold Dust).",
    "Give Kafei's letter to Madame Aroma in the Milk Bar on the Final Night (Chateau Romani).",
    "Gorman's Mystery Milk at Gorman Track (MM3D only).",
)

BOTTLES = Category("bottles", "Bottles", "applications-science-symbolic", tuple(
    Check(f"b_{n}", f"Bottle {n}", BOTTLE_SOURCES[n - 1], lambda s, n=n: s.bottles() >= n)
    for n in range(1, 8)
))

UPGRADES = Category("upgrades", "Upgrades", "go-up-symbolic", (
    Check("u_quiver40", "Large Quiver (40)", "Score 40+ at the Town Shooting Gallery.", lambda s: s.upgrade(0) >= 2),
    Check("u_quiver50", "Largest Quiver (50)", "Score high at the Swamp Shooting Gallery.", lambda s: s.upgrade(0) >= 3),
    Check("u_bag20", "Bomb Bag (20)", "Buy it at the Bomb Shop in West Clock Town.", lambda s: s.upgrade(3) >= 1),
    Check("u_bag30", "Big Bomb Bag (30)", "Bomb Shop or Curiosity Shop (after saving the Bomb Shop lady from Sakon).", lambda s: s.upgrade(3) >= 2),
    Check("u_bag40", "Biggest Bomb Bag (40)", "Sold to Goron Link by a Business Scrub (Goron Village or the Southern Swamp).", lambda s: s.upgrade(3) >= 3),
    Check("u_wallet200", "Adult Wallet", "Deposit 200 rupees at the bank.", lambda s: s.upgrade(12, 2) >= 1),
    Check("u_wallet500", "Giant's Wallet", "Collect all 30 Gold Skulltulas in the Oceanside Spider House (Day 1 is best).", lambda s: s.upgrade(12, 2) >= 2),
    Check("u_razor", "Razor Sword", "Pay the Mountain Village smithy 100 rupees on Day 1 and pick it up on Day 2.", lambda s: s.sword() >= 2),
    Check("u_gilded", "Gilded Sword", "Give the smithy Gold Dust with your Razor Sword in the same cycle.", lambda s: s.sword() >= 3),
    Check("u_mirror", "Mirror Shield", "At the bottom of the Beneath the Well dungeon in Ikana (needs the Gibdo Mask).", lambda s: s.shield() >= 2),
))

_FAIRY_NAMES = ("Woodfall", "Snowhead", "Great Bay", "Stone Tower")


def _fairy_detail(i):
    return lambda s: f"Carrying {s.stray_fairies(i)}/15 stray fairies this cycle"


GREAT_FAIRIES = Category("fairies", "Great Fairies", "weather-clear-night-symbolic", (
    Check("g_clocktown", "Clock Town — Magic", "Bring the Clock Town stray fairy to the Great Fairy in North Clock Town as Deku Link.",
          lambda s: s.u8(OFF_MAGIC_ACQUIRED) != 0),
    Check("g_woodfall", "Woodfall — Great Spin Attack", "Return all 15 Woodfall Temple stray fairies.",
          lambda s: s.week_event(23, 0x02), _fairy_detail(0)),
    Check("g_snowhead", "Snowhead — Double Magic", "Return all 15 Snowhead Temple stray fairies.",
          lambda s: s.u8(OFF_MAGIC_UPGRADES) != 0, _fairy_detail(1)),
    Check("g_greatbay", "Great Bay — Double Defense", "Return all 15 Great Bay Temple stray fairies (fairy fountain at Zora Cape).",
          lambda s: s.u8(OFF_DOUBLE_DEFENSE) != 0, _fairy_detail(2)),
    Check("i_gfsword", "Ikana — Great Fairy's Sword", "Return all 15 Stone Tower Temple stray fairies.",
          lambda s: s.has_item(0x10), _fairy_detail(3)),
))

SPIDER_HOUSES = Category("spiders", "Spider Houses", "emoji-nature-symbolic", (
    Check("m_truth", "Swamp Spider House — Mask of Truth", "Clear out all 30 Gold Skulltulas in the Southern Swamp Spider House.",
          lambda s: s.has_mask(0x36), lambda s: f"{s.skulltulas('swamp')}/30 tokens this cycle"),
    Check("u_wallet500", "Oceanside Spider House — Giant's Wallet", "Clear out all 30 Gold Skulltulas in the Oceanside Spider House.",
          lambda s: s.upgrade(12, 2) >= 2, lambda s: f"{s.skulltulas('ocean')}/30 tokens this cycle"),
))

BOSSES = Category("bosses", "Bosses", "security-high-symbolic", (
    Check("r_odolwa", "Odolwa's Remains", "Beat Odolwa in Woodfall Temple.", lambda s: s.collect(0)),
    Check("r_goht", "Goht's Remains", "Beat Goht in Snowhead Temple.", lambda s: s.collect(1)),
    Check("r_gyorg", "Gyorg's Remains", "Beat Gyorg in Great Bay Temple.", lambda s: s.collect(2)),
    Check("r_twinmold", "Twinmold's Remains", "Beat Twinmold in Stone Tower Temple (inverted).", lambda s: s.collect(3)),
    Check("hc_odolwa", "Heart Container — Odolwa", "Pick it up after beating Odolwa.", lambda s: s.collectible(0x1F, 31)),
    Check("hc_goht", "Heart Container — Goht", "Pick it up after beating Goht.", lambda s: s.collectible(0x44, 31)),
    Check("hc_gyorg", "Heart Container — Gyorg", "Pick it up after beating Gyorg.", lambda s: s.collectible(0x5F, 31)),
    Check("hc_twinmold", "Heart Container — Twinmold", "Pick it up after beating Twinmold.", lambda s: s.collectible(0x36, 31)),
))

_OWLS = (
    (4, "Clock Town"), (5, "Milk Road"), (7, "Southern Swamp"), (6, "Woodfall"),
    (3, "Mountain Village"), (2, "Snowhead"), (0, "Great Bay Coast"), (1, "Zora Cape"),
    (8, "Ikana Canyon"), (9, "Stone Tower"),
)

OWLS = Category("owls", "Owl Statues", "mark-location-symbolic", tuple(
    Check(f"o_{bit}", name, f"Strike the owl statue in {name} with your sword to activate it.",
          lambda s, b=bit: bool(s.u16(OFF_OWLS) >> b & 1))
    for bit, name in _OWLS
))

CATEGORIES: tuple[Category, ...] = (
    MASKS, SONGS, ITEMS, BOTTLES, UPGRADES, GREAT_FAIRIES, SPIDER_HOUSES, BOSSES, OWLS,
)
