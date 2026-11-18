"""Everything besides Pieces of Heart that counts toward 100% in Ocarina of Time 3D.

Offsets are relative to the start of the SaveContext (see oot3d_save.py), from
OoT3D_Randomizer's z3D.h. Gold Skulltula areas and bits come from the
randomizer's item_location.cpp.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable

OFF_MAGIC_ACQUIRED = 0x4E
OFF_DOUBLE_MAGIC = 0x50
OFF_DOUBLE_DEFENSE = 0x51
OFF_BGS_FLAG = 0x52           # 1 = Biggoron's Sword, 0 = Giant's Knife
OFF_ITEMS = 0x8C              # 26 x u8 item ids by slot (0xFF = empty)
OFF_EQUIPMENT = 0xB6          # u16: swords 0-3, shields 4-6, tunics 8-10, boots 12-14
OFF_UPGRADES = 0xB8           # u32: quiver 0-2, bombs 3-5, strength 6-8, scale 9-11,
                              #      wallet 12-13, seeds 14-16, sticks 17-19, nuts 20-22
OFF_QUEST = 0xBC              # u32: medallions 0-5, songs 6-17, stones 18-20, agony 21, card 22
OFF_GS_TOKENS = 0xE8          # s16
OFF_SCENE_FLAGS = 0xEC        # 124 x 0x1C: chest, swch, clear, collect, unk, rooms1, rooms2
SCENE_STRIDE = 0x1C
OFF_GS_FLAGS = 0xEB4          # u8[22], one byte per area
OFF_BIG_POE_POINTS = 0xED4    # u32, 100 per Big Poe sold
OFF_FISHING_FLAGS = 0xED9     # bit 2: record as child, bit 3: record as adult
OFF_EVENT_CHK = 0xEEC         # u16[14]
OFF_ITEM_GET = 0xF08          # u16[4]
OFF_INF_TABLE = 0xF10         # u16[30]


def _swap16(v: int) -> int:
    return ((v & 0xFF00) >> 8) | ((v & 0xFF) << 8)


class SaveView:
    def __init__(self, data: bytes, base: int = 0):
        self.d = data
        self.b = base

    def u8(self, off: int) -> int:
        return self.d[self.b + off]

    def s16(self, off: int) -> int:
        return struct.unpack_from("<h", self.d, self.b + off)[0]

    def u16(self, off: int) -> int:
        return struct.unpack_from("<H", self.d, self.b + off)[0]

    def u32(self, off: int) -> int:
        return struct.unpack_from("<I", self.d, self.b + off)[0]

    # ---- flags ------------------------------------------------------------
    def scene_word(self, scene: int, word: int) -> int:
        return self.u32(OFF_SCENE_FLAGS + scene * SCENE_STRIDE + word * 4)

    def flag(self, f: tuple) -> bool:
        kind = f[0]
        if kind == "coll":
            return bool(self.scene_word(f[1], 3) >> f[2] & 1)
        if kind == "chest":
            return bool(self.scene_word(f[1], 0) >> f[2] & 1)
        if kind == "scrub":
            return bool(self.scene_word(f[1], 4) >> f[2] & 1)
        if kind == "evt":
            return bool(self.u16(OFF_EVENT_CHK + (f[1] >> 4) * 2) >> (f[1] & 0xF) & 1)
        if kind == "igi":
            return bool(_swap16(self.u16(OFF_ITEM_GET + (f[1] // 16) * 2)) >> (f[1] % 16) & 1)
        if kind == "inf":
            return bool(_swap16(self.u16(OFF_INF_TABLE + f[1] * 2)) >> f[2] & 1)
        if kind == "fish":
            return bool(self.u8(OFF_FISHING_FLAGS) >> f[1] & 1)
        if kind == "gs":
            return bool(self.u8(OFF_GS_FLAGS + f[1]) & f[2])
        raise ValueError(f"unknown flag kind {kind!r}")

    # ---- inventory --------------------------------------------------------
    def item(self, slot: int) -> int:
        return self.u8(OFF_ITEMS + slot)

    def has_slot(self, slot: int) -> bool:
        return self.item(slot) != 0xFF

    def equip(self, bit: int) -> bool:
        return bool(self.u16(OFF_EQUIPMENT) >> bit & 1)

    def upgrade(self, shift: int, width: int = 3) -> int:
        return self.u32(OFF_UPGRADES) >> shift & ((1 << width) - 1)

    def quest(self, bit: int) -> bool:
        return bool(self.u32(OFF_QUEST) >> bit & 1)

    def bottles(self) -> int:
        return sum(1 for s in range(18, 22) if self.has_slot(s))


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    hint: str
    test: Callable[[SaveView], bool]
    detail: Callable[[SaveView], str] | None = None
    group: str = ""          # optional sub-heading on the category page


@dataclass(frozen=True)
class Category:
    id: str
    title: str
    icon: str
    checks: tuple[Check, ...]


C = Check

# ---- Quest status -----------------------------------------------------------
QUEST = (
    C("q_emerald", "Kokiri's Emerald", "Beat Queen Gohma in the Great Deku Tree.", lambda v: v.quest(18)),
    C("q_ruby", "Goron's Ruby", "Beat King Dodongo in Dodongo's Cavern.", lambda v: v.quest(19)),
    C("q_sapphire", "Zora's Sapphire", "Beat Barinade inside Jabu-Jabu's Belly.", lambda v: v.quest(20)),
    C("q_forest", "Forest Medallion", "Beat Phantom Ganon in the Forest Temple.", lambda v: v.quest(0)),
    C("q_fire", "Fire Medallion", "Beat Volvagia in the Fire Temple.", lambda v: v.quest(1)),
    C("q_water", "Water Medallion", "Beat Morpha in the Water Temple.", lambda v: v.quest(2)),
    C("q_shadow", "Shadow Medallion", "Beat Bongo Bongo in the Shadow Temple.", lambda v: v.quest(4)),
    C("q_spirit", "Spirit Medallion", "Beat Twinrova in the Spirit Temple.", lambda v: v.quest(3)),
    C("q_light", "Light Medallion", "From Rauru when you first become an adult.", lambda v: v.quest(5)),
    C("q_agony", "Stone of Agony", "Bring 20 Gold Skulltula tokens to the House of Skulltula.",
      lambda v: v.quest(21)),
    C("q_card", "Gerudo's Card", "Rescue all four carpenters in Gerudo's Fortress.", lambda v: v.quest(22)),
)

# ---- Songs --------------------------------------------------------------------
SONGS = (
    C("s_lullaby", "Zelda's Lullaby", "Impa teaches it after you meet Zelda.", lambda v: v.quest(12)),
    C("s_epona", "Epona's Song", "Malon teaches it at Lon Lon Ranch.", lambda v: v.quest(13)),
    C("s_saria", "Saria's Song", "Saria teaches it in the Sacred Forest Meadow.", lambda v: v.quest(14)),
    C("s_sun", "Sun's Song", "On the wall at the end of the Royal Family's Tomb.", lambda v: v.quest(15)),
    C("s_time", "Song of Time", "Zelda teaches it at the castle moat as you get the Ocarina of Time.",
      lambda v: v.quest(16)),
    C("s_storms", "Song of Storms", "Adult: from the man in the Kakariko windmill.", lambda v: v.quest(17)),
    C("s_minuet", "Minuet of Forest", "Sheik, in the Sacred Forest Meadow.", lambda v: v.quest(6)),
    C("s_bolero", "Bolero of Fire", "Sheik, at the entrance to Death Mountain Crater.", lambda v: v.quest(7)),
    C("s_serenade", "Serenade of Water", "Sheik, at the end of the Ice Cavern.", lambda v: v.quest(8)),
    C("s_nocturne", "Nocturne of Shadow", "Sheik, in Kakariko after the Forest, Fire and Water Temples.",
      lambda v: v.quest(10)),
    C("s_requiem", "Requiem of Spirit", "Sheik, at the Desert Colossus.", lambda v: v.quest(9)),
    C("s_prelude", "Prelude of Light", "Sheik, in the Temple of Time after the Forest Medallion.",
      lambda v: v.quest(11)),
)

# ---- Items (inventory slots) --------------------------------------------------
ITEMS = (
    C("i_sticks", "Deku Sticks", "Break Deku Babas or buy them in Kokiri Forest.", lambda v: v.has_slot(0)),
    C("i_nuts", "Deku Nuts", "Dropped by Deku Scrubs and Deku Babas.", lambda v: v.has_slot(1)),
    C("i_bombs", "Bombs", "The Bomb Bag in Dodongo's Cavern.", lambda v: v.has_slot(2)),
    C("i_slingshot", "Fairy Slingshot", "In the Great Deku Tree.", lambda v: v.has_slot(6)),
    C("i_boomerang", "Boomerang", "Inside Jabu-Jabu's Belly.", lambda v: v.has_slot(12)),
    C("i_ocarina", "Ocarina of Time", "Zelda throws it to you at the castle moat.",
      lambda v: v.item(7) == 0x08),
    C("i_bombchus", "Bombchus", "Bombchu Bowling, the Bombchu Shop, or chests.", lambda v: v.has_slot(8)),
    C("i_beans", "Magic Beans", "Buy them from the man near the start of Zora's River.",
      lambda v: v.has_slot(14)),
    C("i_lens", "Lens of Truth", "At the bottom of the Bottom of the Well.", lambda v: v.has_slot(13)),
    C("i_hookshot", "Hookshot", "Adult: win Dampé's race in the Graveyard.", lambda v: v.has_slot(9)),
    C("i_longshot", "Longshot", "In the Water Temple.", lambda v: v.item(9) == 0x0B),
    C("i_bow", "Fairy Bow", "In the Forest Temple.", lambda v: v.has_slot(3)),
    C("i_hammer", "Megaton Hammer", "In the Fire Temple.", lambda v: v.has_slot(15)),
    C("i_fire_arrows", "Fire Arrows", "Adult: shoot an arrow at the rising sun at Lake Hylia.",
      lambda v: v.has_slot(4)),
    C("i_ice_arrows", "Ice Arrows", "Gerudo Training Ground.", lambda v: v.has_slot(10)),
    C("i_light_arrows", "Light Arrows", "From Zelda after both the Shadow and Spirit Medallions.",
      lambda v: v.has_slot(16)),
    C("i_dins", "Din's Fire", "Great Fairy behind the boulder near Hyrule Castle (child).",
      lambda v: v.has_slot(5)),
    C("i_farores", "Farore's Wind", "Great Fairy in Zora's Fountain (child; bomb the wall).",
      lambda v: v.has_slot(11)),
    C("i_nayrus", "Nayru's Love", "Great Fairy at the Desert Colossus (child).", lambda v: v.has_slot(17)),
)

# ---- Equipment ------------------------------------------------------------------
EQUIPMENT = (
    C("e_kokiri_sword", "Kokiri Sword", "In the Kokiri Forest training area; crawl through the hole.",
      lambda v: v.equip(0)),
    C("e_master_sword", "Master Sword", "In the Temple of Time.", lambda v: v.equip(1)),
    C("e_biggoron_sword", "Biggoron's Sword", "Finish the adult trading quest with Biggoron.",
      lambda v: v.equip(2) and v.u8(OFF_BGS_FLAG) != 0),
    C("e_deku_shield", "Deku Shield", "Kokiri Shop. It burns, so buy another if it's gone.",
      lambda v: v.equip(4)),
    C("e_hylian_shield", "Hylian Shield", "Market or Kakariko Bazaar, or a Kakariko grave.",
      lambda v: v.equip(5)),
    C("e_mirror_shield", "Mirror Shield", "In the Spirit Temple.", lambda v: v.equip(6)),
    C("e_goron_tunic", "Goron Tunic", "From Link the Goron in Goron City, or the Goron Shop.",
      lambda v: v.equip(9)),
    C("e_zora_tunic", "Zora Tunic", "Thaw King Zora with Blue Fire.", lambda v: v.equip(10)),
    C("e_iron_boots", "Iron Boots", "At the end of the Ice Cavern.", lambda v: v.equip(13)),
    C("e_hover_boots", "Hover Boots", "In the Shadow Temple.", lambda v: v.equip(14)),
)


def _up(cid, name, hint, shift, level, width=3):
    return C(cid, name, hint, lambda v: v.upgrade(shift, width) >= level)


# ---- Upgrades -------------------------------------------------------------------
EITHER = "whichever of the two you haven't done yet."
UPGRADES = (
    _up("u_quiver40", "Big Quiver (40)", "Adult: win the Kakariko shooting gallery.", 0, 2),
    _up("u_quiver50", "Biggest Quiver (50)", "Adult: 1,500 points at horseback archery.", 0, 3),
    _up("u_bombbag30", "Big Bomb Bag (30)",
        "Child: win Bombchu Bowling, or stop the rolling Goron in Goron City with a bomb.", 3, 2),
    _up("u_bombbag40", "Biggest Bomb Bag (40)", f"Bombchu Bowling or the rolling Goron: {EITHER}", 3, 3),
    _up("u_bracelet", "Goron's Bracelet", "From Darunia after playing Saria's Song.", 6, 1),
    _up("u_silver_gauntlets", "Silver Gauntlets", "Child: in the Spirit Temple.", 6, 2),
    _up("u_golden_gauntlets", "Golden Gauntlets", "In Ganon's Castle, in the Shadow Trial.", 6, 3),
    _up("u_silver_scale", "Silver Scale", "Child: win the diving game in Zora's Domain.", 9, 1),
    _up("u_gold_scale", "Golden Scale", "Adult: catch a big enough fish at the Fishing Pond.", 9, 2),
    _up("u_wallet200", "Adult's Wallet", "10 Gold Skulltula tokens.", 12, 1, 2),
    _up("u_wallet500", "Giant's Wallet", "30 Gold Skulltula tokens.", 12, 2, 2),
    _up("u_seeds40", "Big Bullet Bag (40)",
        "Child: win the Market shooting gallery, or hit the target in the Lost Woods.", 14, 2),
    _up("u_seeds50", "Biggest Bullet Bag (50)", f"Market gallery or Lost Woods target: {EITHER}", 14, 3),
    _up("u_sticks20", "Deku Stick capacity 20",
        "Show the Skull Mask at the Deku Theater, or buy it from the Lost Woods scrub near the bridge.",
        17, 2),
    _up("u_sticks30", "Deku Stick capacity 30", f"Deku Theater or the bridge scrub: {EITHER}", 17, 3),
    _up("u_nuts30", "Deku Nut capacity 30",
        "Show the Mask of Truth at the Deku Theater, or buy it from the scrub in a Lost Woods grotto.",
        20, 2),
    _up("u_nuts40", "Deku Nut capacity 40", f"Deku Theater or the grotto scrub: {EITHER}", 20, 3),
    C("u_magic", "Magic Meter", "Great Fairy at the summit of Death Mountain.",
      lambda v: v.u8(OFF_MAGIC_ACQUIRED) != 0),
    C("u_double_magic", "Double Magic", "Adult: Great Fairy in Death Mountain Crater.",
      lambda v: v.u8(OFF_DOUBLE_MAGIC) != 0),
    C("u_double_defense", "Double Defense", "Adult: Great Fairy outside Ganon's Castle.",
      lambda v: v.u8(OFF_DOUBLE_DEFENSE) != 0),
)

# ---- Bottles --------------------------------------------------------------------
_BOTTLE_SOURCES = (
    ("Bottle from Talon", "Child: win Talon's cucco game at Lon Lon Ranch."),
    ("Bottle from Anju", "Child: return all seven cuccos to the cucco lady in Kakariko."),
    ("Ruto's Letter", "Find the bottle with Ruto's Letter in Lake Hylia (child)."),
    ("Bottle for 10 Big Poes", "Adult: sell 10 Big Poes to the Poe Collector in the Market guard house."),
)
BOTTLES = tuple(
    C(f"b_{i + 1}", name, hint, (lambda n: lambda v: v.bottles() >= n)(i + 1),
      (lambda v: f"{v.bottles()} of 4 bottles · Big Poe points {v.u32(OFF_BIG_POE_POINTS)}/1000")
      if i == 3 else (lambda v: f"{v.bottles()} of 4 bottles"))
    for i, (name, hint) in enumerate(_BOTTLE_SOURCES)
)

# ---- Heart Containers -----------------------------------------------------------
BOSSES = tuple(
    C(f"r_{key}", f"{boss} Heart Container", where,
      (lambda s: lambda v: v.flag(("coll", s, 0x1F)))(scene))
    for key, boss, where, scene in (
        ("gohma", "Queen Gohma", "Inside the Great Deku Tree.", 0x11),
        ("king_dodongo", "King Dodongo", "Dodongo's Cavern.", 0x12),
        ("barinade", "Barinade", "Inside Jabu-Jabu's Belly.", 0x13),
        ("phantom_ganon", "Phantom Ganon", "Forest Temple.", 0x14),
        ("volvagia", "Volvagia", "Fire Temple.", 0x15),
        ("morpha", "Morpha", "Water Temple.", 0x16),
        ("bongo_bongo", "Bongo Bongo", "Shadow Temple.", 0x18),
        ("twinrova", "Twinrova", "Spirit Temple.", 0x17),
    )
)

# ---- Skulltula House rewards ----------------------------------------------------
SKULLTULA_HOUSE = tuple(
    # ids match the matching item check, so the overall count includes each reward once
    C(cid, f"{n} tokens: {reward}", "House of Skulltula in Kakariko.",
      (lambda f: lambda v: v.flag(("evt", f)))(flag),
      (lambda v: f"{v.s16(OFF_GS_TOKENS)} tokens so far"))
    for cid, n, reward, flag in (
        ("u_wallet200", 10, "Adult's Wallet", 0xDA),
        ("q_agony", 20, "Stone of Agony", 0xDB),
        ("u_wallet500", 30, "Giant's Wallet", 0xDC),
        ("k_40", 40, "Bombchus", 0xDD),
        ("hp_kak_50_skulltulas", 50, "Piece of Heart", 0xDE),
    )
)

# ---- Gold Skulltulas ------------------------------------------------------------
GS_AREAS = {
    0x00: "Inside the Deku Tree", 0x01: "Dodongo's Cavern", 0x02: "Jabu-Jabu's Belly",
    0x03: "Forest Temple", 0x04: "Fire Temple", 0x05: "Water Temple", 0x06: "Spirit Temple",
    0x07: "Shadow Temple", 0x08: "Bottom of the Well", 0x09: "Ice Cavern",
    0x0A: "Hyrule Field", 0x0B: "Lon Lon Ranch", 0x0C: "Kokiri Forest",
    0x0D: "Lost Woods & Sacred Forest Meadow", 0x0E: "Market, Hyrule Castle & Ganon's Castle",
    0x0F: "Death Mountain & Goron City", 0x10: "Kakariko & Graveyard",
    0x11: "Zora's River, Domain & Fountain", 0x12: "Lake Hylia", 0x13: "Gerudo Valley",
    0x14: "Gerudo's Fortress", 0x15: "Haunted Wasteland & Desert Colossus",
}
# Overworld groups shown first, dungeons after.
GS_ORDER = [0x0C, 0x0D, 0x0A, 0x0B, 0x0E, 0x10, 0x0F, 0x11, 0x12, 0x13, 0x14, 0x15,
            0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09]

BEAN = "Child: drop bugs from a bottle onto the soft soil."
# (id, area, mask, name, hint) — vanilla
GS_VANILLA = [
    ("kf_bean_patch", 0x0C, 0x01, "Soft soil patch", BEAN),
    ("kf_know_it_all", 0x0C, 0x02, "Know-It-All Brothers' house", "Child, at night: on the back of the house."),
    ("kf_twins", 0x0C, 0x04, "House of Twins", "Adult, at night: on the side of the twins' house (Hookshot)."),
    ("lw_bean_bridge", 0x0D, 0x01, "Soft soil near the bridge", BEAN),
    ("lw_bean_theater", 0x0D, 0x02, "Soft soil near the Deku Theater", BEAN),
    ("lw_above_theater", 0x0D, 0x04, "Above the Deku Theater", "Adult, at night: ride the bean plant up."),
    ("sfm", 0x0D, 0x08, "Sacred Forest Meadow maze", "Adult, at night: on a maze wall (Hookshot)."),
    ("hf_cow_grotto", 0x0A, 0x01, "Cow grotto", "Inside the grotto with the cow; burn the web."),
    ("hf_near_kak", 0x0A, 0x02, "Grotto near Kakariko", "Inside the hidden grotto near the Kakariko path."),
    ("llr_back_wall", 0x0B, 0x01, "Back wall", "Child, at night: on the ranch's outer wall."),
    ("llr_rain_shed", 0x0B, 0x02, "Rain shed", "Child, at night: on the shed by the stables."),
    ("llr_window", 0x0B, 0x04, "House window", "Child, at night: by a window of the ranch house."),
    ("llr_tree", 0x0B, 0x08, "Tree", "Child: roll into the tree."),
    ("mk_guard_house", 0x0E, 0x08, "Guard house crate", "Child: in a crate in the Market guard house."),
    ("hc_tree", 0x0E, 0x04, "Castle grounds tree", "Child: roll into the tree near the castle."),
    ("hc_storms_grotto", 0x0E, 0x02, "Song of Storms grotto", "Child: play the Song of Storms at the lone "
                                                                "rock near the castle, then bomb the wall."),
    ("ogc", 0x0E, 0x01, "Outside Ganon's Castle", "Adult: on the pillar by the castle."),
    ("kak_tree", 0x10, 0x20, "Tree by the entrance", "Child: roll into the tree."),
    ("kak_construction", 0x10, 0x08, "House under construction", "Child, at night: on the house's wall."),
    ("kak_skulltula_house", 0x10, 0x10, "House of Skulltula", "Child, at night: on the back of the house."),
    ("kak_guards_house", 0x10, 0x02, "Guard's house", "Child, at night: on the guard's house."),
    ("kak_watchtower", 0x10, 0x04, "Watchtower", "Child, at night: on the watchtower's ladder."),
    ("kak_above_impa", 0x10, 0x40, "Above Impa's house", "Adult, at night: on the wall above Impa's house."),
    ("gy_wall", 0x10, 0x80, "Graveyard wall", "Child, at night: on the back wall (Boomerang)."),
    ("gy_bean", 0x10, 0x01, "Graveyard soft soil", BEAN),
    ("dmt_bean", 0x0F, 0x02, "Trail soft soil", BEAN),
    ("dmt_near_kak", 0x0F, 0x04, "Near Kakariko", "Child: break the rock near the bottom of the trail."),
    ("dmt_above_cavern", 0x0F, 0x08, "Above Dodongo's Cavern", "Adult, at night: on the wall above the "
                                                               "cavern (Megaton Hammer the rock)."),
    ("dmt_falling_rocks", 0x0F, 0x10, "Falling rocks path", "Adult, at night: on the path to the summit."),
    ("dmc_bean", 0x0F, 0x01, "Crater soft soil", BEAN),
    ("dmc_crate", 0x0F, 0x80, "Crater crate", "Child: in a crate near the crater's entrance."),
    ("gc_center", 0x0F, 0x20, "Goron City center platform", "Adult: on the platform in the middle."),
    ("gc_boulder_maze", 0x0F, 0x40, "Goron City boulder maze", "Child: inside a crate in the boulder maze."),
    ("zr_tree", 0x11, 0x02, "Zora's River tree", "Child: roll into the tree near the entrance."),
    ("zr_ladder", 0x11, 0x01, "Ladder", "Child, at night: on the ladder along the river."),
    ("zr_above_bridge", 0x11, 0x08, "Above the bridge", "Adult, at night: on the wall above the bridge."),
    ("zr_raised_grottos", 0x11, 0x10, "Near the raised grottos", "Adult, at night: on the wall by the grottos."),
    ("zd_waterfall", 0x11, 0x40, "Frozen waterfall", "Adult, at night: at the top of Zora's Domain."),
    ("zf_tree", 0x11, 0x80, "Zora's Fountain tree", "Child: roll into the tree."),
    ("zf_above_log", 0x11, 0x04, "Above the log", "Child, at night: on the wall above the log."),
    ("zf_hidden_cave", 0x11, 0x20, "Hidden cave", "Adult: lift the silver rock, then bomb into the cave."),
    ("lh_bean", 0x12, 0x01, "Lake Hylia soft soil", BEAN),
    ("lh_small_island", 0x12, 0x02, "Small island", "Child, at night: on the small island."),
    ("lh_lab_wall", 0x12, 0x04, "Laboratory wall", "Child, at night: on the lab's wall (Boomerang)."),
    ("lh_lab_crate", 0x12, 0x08, "Laboratory crate", "Adult: in a crate at the bottom of the lab's pool."),
    ("lh_tree", 0x12, 0x10, "Island tree", "Adult, at night: high up in the tree (Longshot)."),
    ("gv_bean", 0x13, 0x01, "Gerudo Valley soft soil", BEAN),
    ("gv_small_bridge", 0x13, 0x02, "Small bridge", "Child, at night: near the small bridge."),
    ("gv_pillar", 0x13, 0x04, "Pillar", "Adult, at night: on a rock pillar (Hookshot)."),
    ("gv_behind_tent", 0x13, 0x08, "Behind the tent", "Adult, at night: behind the carpenters' tent."),
    ("gf_archery", 0x14, 0x01, "Archery range", "Adult, at night: on a target at the archery range."),
    ("gf_top_floor", 0x14, 0x02, "Fortress top floor", "Adult, at night: on top of the fortress."),
    ("wasteland", 0x15, 0x02, "Wasteland structure", "Adult: inside the stone structure halfway across."),
    ("colossus_bean", 0x15, 0x01, "Colossus soft soil", BEAN),
    ("colossus_hill", 0x15, 0x04, "Colossus hill", "Adult, at night: on the hill (bean plant or Longshot)."),
    ("colossus_tree", 0x15, 0x08, "Colossus tree", "Adult, at night: on a tree near the oasis."),
]
GS_DUNGEONS = {
    False: [
        ("dt_basement_back", 0x00, 0x01, "Basement back room"),
        ("dt_basement_gate", 0x00, 0x02, "Basement gate"),
        ("dt_basement_vines", 0x00, 0x04, "Basement vines"),
        ("dt_compass_room", 0x00, 0x08, "Compass room"),
        ("dc_vines_stairs", 0x01, 0x01, "Vines above the stairs"),
        ("dc_scarecrow", 0x01, 0x02, "Scarecrow"),
        ("dc_alcove_stairs", 0x01, 0x04, "Alcove above the stairs"),
        ("dc_back_room", 0x01, 0x08, "Back room"),
        ("dc_side_room", 0x01, 0x10, "Side room near the lower Lizalfos"),
        ("jabu_basement_lower", 0x02, 0x01, "Lobby basement, lower"),
        ("jabu_basement_upper", 0x02, 0x02, "Lobby basement, upper"),
        ("jabu_near_boss", 0x02, 0x04, "Near the boss"),
        ("jabu_water_switch", 0x02, 0x08, "Water switch room"),
        ("ft_raised_courtyard", 0x03, 0x01, "Raised island courtyard"),
        ("ft_first_room", 0x03, 0x02, "First room"),
        ("ft_level_courtyard", 0x03, 0x04, "Level island courtyard"),
        ("ft_lobby", 0x03, 0x08, "Lobby"),
        ("ft_basement", 0x03, 0x10, "Basement"),
        ("fire_sot_room", 0x04, 0x01, "Song of Time room"),
        ("fire_boss_key_loop", 0x04, 0x02, "Boss key loop"),
        ("fire_boulder_maze", 0x04, 0x04, "Boulder maze"),
        ("fire_scarecrow_top", 0x04, 0x08, "Scarecrow, top"),
        ("fire_scarecrow_climb", 0x04, 0x10, "Scarecrow climb"),
        ("water_behind_gate", 0x05, 0x01, "Behind the gate"),
        ("water_falling_platform", 0x05, 0x02, "Falling platform room"),
        ("water_central_pillar", 0x05, 0x04, "Central pillar"),
        ("water_near_boss_key", 0x05, 0x08, "Near the boss key chest"),
        ("water_river", 0x05, 0x10, "River"),
        ("spirit_after_sun_block", 0x06, 0x01, "Hall after the sun block room"),
        ("spirit_boulder_room", 0x06, 0x02, "Boulder room"),
        ("spirit_lobby", 0x06, 0x04, "Lobby"),
        ("spirit_sun_floor", 0x06, 0x08, "Sun on the floor room"),
        ("spirit_metal_fence", 0x06, 0x10, "Metal fence"),
        ("shadow_single_pot", 0x07, 0x01, "Single giant pot"),
        ("shadow_falling_spikes", 0x07, 0x02, "Falling spikes room"),
        ("shadow_triple_pot", 0x07, 0x04, "Triple giant pot"),
        ("shadow_like_like", 0x07, 0x08, "Like Like room"),
        ("shadow_near_ship", 0x07, 0x10, "Near the ship"),
        ("botw_like_like_cage", 0x08, 0x01, "Like Like cage"),
        ("botw_east_inner", 0x08, 0x02, "East inner room"),
        ("botw_west_inner", 0x08, 0x04, "West inner room"),
        ("ice_push_block", 0x09, 0x01, "Push block room"),
        ("ice_scythe_room", 0x09, 0x02, "Spinning scythe room"),
        ("ice_heart_piece_room", 0x09, 0x04, "Heart Piece room"),
    ],
    True: [
        ("dt_mq_lobby", 0x00, 0x02, "Lobby"),
        ("dt_mq_compass_room", 0x00, 0x08, "Compass room"),
        ("dt_mq_graves_room", 0x00, 0x04, "Basement graves room"),
        ("dt_mq_basement_back", 0x00, 0x01, "Basement back room"),
        ("dc_mq_scrub_room", 0x01, 0x02, "Scrub room"),
        ("dc_mq_sot_room", 0x01, 0x08, "Song of Time block room"),
        ("dc_mq_lizalfos_room", 0x01, 0x04, "Lizalfos room"),
        ("dc_mq_larvae_room", 0x01, 0x10, "Larvae room"),
        ("dc_mq_back_area", 0x01, 0x01, "Back room"),
        ("jabu_mq_tailpasaran", 0x02, 0x04, "Tailpasaran room"),
        ("jabu_mq_invisible", 0x02, 0x08, "Invisible enemies room"),
        ("jabu_mq_boomerang", 0x02, 0x01, "Boomerang chest room"),
        ("jabu_mq_near_boss", 0x02, 0x02, "Near the boss"),
        ("ft_mq_first_hallway", 0x03, 0x02, "First hallway"),
        ("ft_mq_block_push", 0x03, 0x10, "Block push room"),
        ("ft_mq_raised_courtyard", 0x03, 0x01, "Raised island courtyard"),
        ("ft_mq_level_courtyard", 0x03, 0x04, "Level island courtyard"),
        ("ft_mq_well", 0x03, 0x08, "Well"),
        ("fire_mq_above_maze", 0x04, 0x02, "Above the fire wall maze"),
        ("fire_mq_maze_center", 0x04, 0x08, "Fire wall maze center"),
        ("fire_mq_lava_room", 0x04, 0x01, "Big lava room, open door"),
        ("fire_mq_maze_side", 0x04, 0x10, "Fire wall maze side room"),
        ("fire_mq_skull_on_fire", 0x04, 0x04, "Skull on fire"),
        ("water_mq_upper_switch", 0x05, 0x04, "Before the upper water switch"),
        ("water_mq_key_area", 0x05, 0x08, "Freestanding key area"),
        ("water_mq_lizalfos", 0x05, 0x01, "Lizalfos hallway"),
        ("water_mq_river", 0x05, 0x02, "River"),
        ("water_mq_triple_torch", 0x05, 0x10, "Triple wall torch"),
        ("spirit_mq_symphony", 0x06, 0x08, "Symphony room"),
        ("spirit_mq_leever", 0x06, 0x02, "Leever room"),
        ("spirit_mq_thrones_west", 0x06, 0x04, "Nine thrones room, west"),
        ("spirit_mq_thrones_north", 0x06, 0x10, "Nine thrones room, north"),
        ("spirit_mq_sun_block", 0x06, 0x01, "Sun block room"),
        ("shadow_mq_falling_spikes", 0x07, 0x02, "Falling spikes room"),
        ("shadow_mq_wind_hint", 0x07, 0x01, "Wind hint room"),
        ("shadow_mq_after_wind", 0x07, 0x08, "After the wind"),
        ("shadow_mq_after_ship", 0x07, 0x10, "After the ship"),
        ("shadow_mq_near_boss", 0x07, 0x04, "Near the boss"),
        ("botw_mq_basement", 0x08, 0x01, "Basement"),
        ("botw_mq_coffin_room", 0x08, 0x04, "Coffin room"),
        ("botw_mq_west_inner", 0x08, 0x02, "West inner room"),
        ("ice_mq_scarecrow", 0x09, 0x01, "Scarecrow"),
        ("ice_mq_ice_block", 0x09, 0x04, "Ice block"),
        ("ice_mq_red_ice", 0x09, 0x02, "Red ice"),
    ],
}


def gold_skulltulas(mq: bool) -> tuple[Check, ...]:
    entries = list(GS_VANILLA) + [(i, a, m, n, "") for i, a, m, n in GS_DUNGEONS[mq]]
    entries.sort(key=lambda e: GS_ORDER.index(e[1]))
    tokens = lambda v: f"{v.s16(OFF_GS_TOKENS)} tokens collected"  # noqa: E731
    return tuple(
        C(f"gs_{gid}", name, hint, (lambda a, m: lambda v: v.flag(("gs", a, m)))(area, mask),
          tokens, group=GS_AREAS[area])
        for gid, area, mask, name, hint in entries
    )


assert len(gold_skulltulas(False)) == 100 and len(gold_skulltulas(True)) == 100


def build_categories(mq: bool = False) -> list[Category]:
    return [
        Category("gold_skulltulas", "Gold Skulltulas", "emoji-nature-symbolic", gold_skulltulas(mq)),
        Category("skulltula_house", "Skulltula House rewards", "avatar-default-symbolic", SKULLTULA_HOUSE),
        Category("bosses", "Heart Containers", "emblem-favorite-symbolic", BOSSES),
        Category("quest", "Stones & Medallions", "starred-symbolic", QUEST),
        Category("songs", "Songs", "audio-x-generic-symbolic", SONGS),
        Category("items", "Items", "view-grid-symbolic", ITEMS),
        Category("equipment", "Equipment", "security-high-symbolic", EQUIPMENT),
        Category("upgrades", "Upgrades", "go-up-symbolic", UPGRADES),
        Category("bottles", "Bottles", "applications-science-symbolic", BOTTLES),
    ]
