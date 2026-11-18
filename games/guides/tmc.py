"""Step-by-step guide for The Minish Cap. Locations come from the Minish Cap Randomizer's logic
(games/guides/tmc_data.py, generated)."""

from .tmc_data import HEART_CONTAINERS, HEART_PIECE_STEPS, ITEM_LOCATIONS


def _loc(key: str, n: int = 0) -> tuple[str, ...]:
    spots = ITEM_LOCATIONS.get(key, [])
    return tuple(spots[n][2]) if len(spots) > n else ()


ITEM_KEYS = {
    "it_01": "@SMITHSWORD", "it_09": "@BOW", "it_0b": "@BOOMERANG", "it_0d": "@SHIELD",
    "it_0f": "Lantern", "it_11": "GustJar", "it_12": "PacciCane", "it_13": "MoleMitts", "it_14": "RocsCape",
    "it_15": "PegasusBoots", "it_17": "Ocarina", "it_44": "GripRing", "it_45": "PowerBracelets", "it_46": "Flippers",
    "it_02": "@GREENSWORD", "it_03": "@REDSWORD", "it_04": "@BLUESWORD", "it_06": "@FOURSWORD",
    "it_08": "RemoteBombs", "it_0a": "@LIGHTARROW", "it_0c": "@MAGICBOOMERANG", "it_0e": "@MIRROR",
    "el_40": "EarthElement", "el_41": "FireElement", "el_42": "WaterElement", "el_43": "WindElement",
    "sc_48": "@SPINATTACK", "sc_49": "RollAttack", "sc_4a": "DashAttack", "sc_4b": "RockBreaker",
    "sc_4c": "SwordBeam", "sc_4d": "@GREATSPIN", "sc_4e": "DownThrust", "sc_4f": "PerilBeam",
    "sc_73": "@FASTSPIN", "sc_74": "@FASTSPLIT", "sc_75": "@LONGSPIN",
    "bf_70": "ArrowButterfly", "bf_71": "DigButterfly", "bf_72": "SwimButterfly",
}
GENERATED = {
    **HEART_PIECE_STEPS,
    **{rid: _loc(key) for rid, key in ITEM_KEYS.items() if _loc(key)},
    **{f"up_wallet{n + 1}": _loc("Wallet", n) for n in range(3)},
    **{f"up_bombs{i + 1}": st for i, st in enumerate(
        [tuple(sp[2]) for sp in ITEM_LOCATIONS.get("BombBag", []) if "bomb-making" not in sp[1]][:3])},
    "it_07": next((tuple(sp[2]) for sp in ITEM_LOCATIONS.get("BombBag", []) if "bomb-making" in sp[1]), ()),
    **{f"up_quiver{n + 1}": _loc("LargeQuiver", n) for n in range(2)},
    **{f"bt_{n + 1}": _loc("Bottle", n) for n in range(4)},
    **{f"hc_{i + 1}": tuple(st) for i, (_a, _n, st) in enumerate(HEART_CONTAINERS)},
}


STEPS = {
    **{k: v for k, v in GENERATED.items() if v},
    "el_40": ("Go into Deepwood Shrine in the Minish Woods.", "Beat Big Green ChuChu; the Earth Element is behind it."),
    "el_41": ("Go into the Cave of Flames on Mt. Crenel.", "Beat Gleerok; the Fire Element is behind it."),
    "el_42": ("Go into the Temple of Droplets in Lake Hylia.", "Beat Big Octorok; the Water Element is behind it."),
    "el_43": ("Go up to the Palace of Winds in the Cloud Tops.", "Beat Gyorg Pair; the Wind Element is behind it."),
    "it_01": ("Watch the opening at the Smith's house in Hyrule Town.", "The Smith gives you his sword after the festival."),

    "it_0f": ("It's in the Temple of Droplets, partway through.",),
    "it_11": ("It's the main item of Deepwood Shrine.",),
    "it_12": ("It's the main item of the Cave of Flames.",),
    "it_13": ("It's the main item of the Fortress of Winds.",),
    "it_14": ("It's the main item of the Palace of Winds.",),
    "it_17": ("Finish the Fortress of Winds.", "Ezlo's story leads you to the Ocarina of Wind afterwards."),
    "it_02": ("Finish the Cave of Flames on Mt. Crenel.", "Melari the Minish blacksmith re-forges the Picori Blade into the White Sword."),
    "it_03": ("Infuse the Fire Element at the Elemental Sanctuary.",),
    "it_04": ("Infuse the Water Element at the Elemental Sanctuary.",),
    "it_06": ("Infuse the Wind Element at the Elemental Sanctuary.", "The sword becomes the Four Sword."),
    "it_0e": ("Climb to Biggoron on Veil Falls.", "Let him eat your shield, then come back later.",
              "He gives you the Mirror Shield in return."),
}

SECTIONS = {
    "hearts": (
        "There are 44 Pieces of Heart (4 per heart); 6 more hearts are Heart Containers (5 bosses and Librari).",
        "Each piece below has its own steps. Many are behind Kinstone fusions, in caves, minigames and dojos.",
        "Your save only keeps the heart total, so the tracker can't tick off individual pieces; "
        "use the count at the top to see how many you still need.",
    ),
    "figurines": (
        "Go to Carlov's figurine gallery in Hyrule Town.",
        "Feed Mysterious Shells into his machine; the more you put in, the better the chance of a new figurine.",
        "New figurines become available as the story moves on, so check back after each dungeon.",
    ),
    "fusions": (
        "People and objects with a thought bubble over them want to fuse Kinstones.",
        "Pick the matching half from your Kinstone Bag to complete the fusion.",
        "There are 100 fusions; many open paths, reveal chests or grow beanstalks.",
    ),
    "items": (
        "Dungeon items are each dungeon's main treasure: Gust Jar (Deepwood Shrine), Cane of Pacci "
        "(Cave of Flames), Mole Mitts (Fortress of Winds), Lantern (Temple of Droplets), Roc's Cape (Palace of Winds).",
        "Most of the rest (Bombs, Bow, Boomerang, Pegasus Boots, Grip Ring, Power Bracelets, Flippers, "
        "Kinstone Bag) come from the story, shops and Minish areas between dungeons.",
    ),
    "upgrades": (
        "Sword upgrades: infuse each Element at the Elemental Sanctuary in Hyrule Castle's garden.",
        "Item upgrades (Remote Bombs, Light Arrows, Magical Boomerang) come from side quests and fusions later on.",
        "Wallets, Bomb Bags and Quivers come from side quests, Business Scrubs and fusions.",
    ),
    "bottles": (
        "There are 4 bottles. They come from side quests and Kinstone fusions around Hyrule Town.",
    ),
}
