"""Step-by-step guide for The Minish Cap."""

BLADE = ("Find the Blade Brothers' dojos around Hyrule (Swiftblade's is in Hyrule Town).",
         "Each brother teaches a technique; talk to him and pass his test. Some only teach you once "
         "you have enough hearts.")

STEPS = {
    "el_40": ("Go into Deepwood Shrine in the Minish Woods.", "Beat Big Green ChuChu; the Earth Element is behind it."),
    "el_41": ("Go into the Cave of Flames on Mt. Crenel.", "Beat Gleerok; the Fire Element is behind it."),
    "el_42": ("Go into the Temple of Droplets in Lake Hylia.", "Beat Big Octorok; the Water Element is behind it."),
    "el_43": ("Go up to the Palace of Winds in the Cloud Tops.", "Beat Gyorg Pair; the Wind Element is behind it."),
    "it_01": ("Watch the opening at the Smith's house in Hyrule Town.", "The Smith gives you his sword after the festival."),
    "it_0d": ("Buy the shield at Stockwell's shop in Hyrule Town.",),
    "it_0f": ("It's in the Temple of Droplets, partway through.",),
    "it_11": ("It's the main item of Deepwood Shrine.",),
    "it_12": ("It's the main item of the Cave of Flames.",),
    "it_13": ("It's the main item of the Fortress of Winds.",),
    "it_14": ("It's the main item of the Palace of Winds.",),
    "it_17": ("Finish the Fortress of Winds.", "Ezlo's story leads you to the Ocarina of Wind afterwards."),
    "it_02": ("Take the Earth Element to the Elemental Sanctuary in Hyrule Castle's garden.",
              "Infuse it into your sword to make the White Sword."),
    "it_03": ("Infuse the Fire Element at the Elemental Sanctuary.",),
    "it_04": ("Infuse the Water Element at the Elemental Sanctuary.",),
    "it_06": ("Infuse the Wind Element at the Elemental Sanctuary.", "The sword becomes the Four Sword."),
    "it_0e": ("Climb to Biggoron on Veil Falls.", "Let him eat your shield, then come back later.",
              "He gives you the Mirror Shield in return."),
    **{f"sc_{i:02x}": BLADE for i in (0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F)},
    **{f"sc_{i:02x}": ("This scroll is hidden in the world, not taught at a dojo.",
                       "Look for it after you've learned the basic techniques.") for i in (0x73, 0x74, 0x75)},
    **{f"bf_{i:02x}": ("A butterfly appears after certain Kinstone fusions.", "Catch it to gain its ability.")
       for i in (0x70, 0x71, 0x72)},
    **{f"up_wallet{n}": ("Wallet upgrades come from side quests and Kinstone fusions.",) for n in (1, 2, 3)},
    **{f"up_bombs{n}": ("Bomb Bag upgrades come from Business Scrubs and side quests.",) for n in (1, 2, 3)},
    **{f"up_quiver{n}": ("Quiver upgrades come from side quests and Kinstone fusions.",) for n in (1, 2)},
}

SECTIONS = {
    "hearts": (
        "6 hearts come from beating the bosses of the first six dungeons.",
        "The other 11 come from 44 Pieces of Heart (4 per heart). Many are behind Kinstone fusions, "
        "in caves, minigames and dojos.",
        "The save only stores your total, so this list fills in as your hearts go up.",
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
