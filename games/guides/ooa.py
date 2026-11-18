"""Step-by-step guide for Oracle of Ages. Item locations from oracles-randomizer-ng's vanilla slot data."""

DUNGEONS = ["Spirit's Grave", "Wing Dungeon", "Moonlit Grotto", "Skull Dungeon",
            "Crown Dungeon", "Mermaid's Cave", "Jabu-Jabu's Belly", "Ancient Tomb"]
BOSSES = ["Pumpkin Head", "Head Thwomp", "Shadow Hag", "Eyesoar", "Smog", "Octogon", "Plasmarine", "Ramrock"]


def dungeon_item(n: int, where: str = "") -> tuple[str, ...]:
    return (f"Go into {DUNGEONS[n - 1]} (Level {n}).",
            f"It's in the {where}." if where else "It's the dungeon's main item, found partway through.")


STEPS = {
    "hp_crescent": ("Get to Crescent Island in the present.", "Find the cave under the island and open the chest."),
    "hp_hidden_shop": ("Find the hidden shop in Lynna City.", "Buy the Piece of Heart there."),
    "hp_maple": ("Kill enemies until Maple flies by on her broom (about every 30 kills).",
                 "Bump into her; she drops items. The Piece of Heart is one of them, usually on a later meeting.",
                 "Pick it up before she grabs it back."),
    "hp_gasha": ("Plant Gasha Seeds in soft soil around Labrynna.", "Kill enemies until each tree grows, then cut the Gasha Nut.",
                 "One nut gives a Piece of Heart (more likely once the tree has matured a lot)."),
    **{f"hc_{i}": (f"Beat {BOSSES[i - 1]} at the end of {DUNGEONS[i - 1]} (Level {i}).",
                   "Pick up the Heart Container before taking the essence.") for i in range(1, 9)},
    **{f"es_{i}": (f"Go into {DUNGEONS[i - 1]} (Level {i}).", f"Get the boss key and beat {BOSSES[i - 1]}.",
                   "The essence is in the room behind the boss.") for i in range(1, 9)},
    "it_sword": ("You start the game with the Wooden Sword.",),
    "it_shield": ("Buy it at the Lynna City shop for 30 Rupees.",),
    "it_bombs": ("Pick them up in the early dungeons or buy them.",),
    "it_satchel": ("Talk to the Maku Tree in Lynna City.", "She gives you the Seed Satchel."),
    "it_ember": ("Get the Seed Satchel.", "Cut the seed tree in South Lynna."),
    "it_scent": ("Get the Seed Satchel.", "Cut the seed tree on Crescent Island (or in Ambi's Palace)."),
    "it_pegasus": ("Get the Seed Satchel.", "Cut the seed tree on the west side of Rolling Ridge."),
    "it_gale": ("Get the Seed Satchel.", "Cut the seed tree in Symmetry City (or Zora Village)."),
    "it_mystery": ("Get the Seed Satchel.", "Cut the seed tree in Deku Forest (or east Rolling Ridge)."),
    "it_bracelet": dungeon_item(1, "basement"),
    "it_shovel": ("Talk to the worker at the Black Tower construction site.", "He gives you the Shovel."),
    "it_feather": dungeon_item(2, "Thwomp tunnel"),
    "it_flute": ("Buy the animal flute at the Lynna City shop (150 Rupees), or get it from your animal companion.",),
    "it_ringbox": ("Visit Vasu's ring shop in Lynna City.", "He gives you the Ring Box and the Friendship Ring."),
    "it_bombchus": ("They show up later in the game, in chests and shops.",),
    "it_biggoron": ("Finish the trading sequence.", "Bring the last trade item to Biggoron to get his sword."),
    "it_shooter": dungeon_item(3, "room with the Mimics"),
    "it_hook": dungeon_item(4, "small floor puzzle room"),
    "it_cane": dungeon_item(5, "six-statue puzzle room"),
    "it_harp": ("Visit Nayru's house in the present at the start.", "Take the Harp of Ages; it comes with the Tune of Echoes."),
    "it_suit": dungeon_item(6, "Vire chest in the present half"),
    "up_sword2": ("Defeat the Poe in the graveyard (Yoll Graveyard).", "It leads you to the Noble Sword."),
    "up_sword3": ("The Master Sword is a linked-game reward.",),
    "up_shield2": ("Find the hidden Tokay cave on Crescent Island.", "The Iron Shield is inside."),
    "up_shield3": ("The Mirror Shield is the final shield upgrade, from the linked game.",),
    "up_satchel2": ("Pay the balloon guy for his upgrade after he gives you the Island Chart.",),
    "up_satchel3": ("A later satchel upgrade; look for it after the first one.",),
    "up_bombs": ("Upgrade your bomb bag later in the game (shops or secrets).",),
    "up_ringbox2": ("Buy the Ring Box upgrade at the hidden shop in Lynna City.",),
    "up_ringbox3": ("The largest Ring Box comes from the linked game.",),
    "up_hook2": dungeon_item(7, "miniboss chest"),
    "up_bracelet2": dungeon_item(8, "floor puzzle room"),
    "tu_echoes": ("Comes with the Harp of Ages in Nayru's house.",),
    "tu_currents": ("Rescue Nayru from Veran.", "She teaches you the Tune of Currents."),
    "tu_ages": ("Help Tokkey with his composition on Crescent Island.", "He teaches you the Tune of Ages."),
}

SECTIONS = {
    "hearts": ("The named pieces are read from your save.",
               "The other pieces are counted from your heart total; look for pieces in caves, in the past "
               "and present versions of each area, and in the side games."),
    "rings": (
        "Rings come out of Gasha Nuts, chests and secrets, and show up unappraised.",
        "Take unappraised rings to Vasu's ring shop in Lynna City to appraise them.",
        "Fixed rings include: Power Ring L-1 and Discovery Ring (Spirit's Grave), Green Holy Ring (Fairies' Coast chest), "
        "Whimsical Ring (Zora Seas chest), Armor Ring L-1 (under Moblin Keep), Light Ring L-1 (Nuun Highlands cave), "
        "Green Luck Ring (Mayor Plen's house), Gold Joy Ring (Goron's hiding place), Blue Ring (Sea of No Return), "
        "Pegasus Ring (Sea of Storms, past), Gold Luck Ring (Ambi's Palace chest), Like Like Ring (Jabu-Jabu's Belly).",
        "Some rings only come from linked games, the Ring secrets, or the GBA bonus.",
    ),
}
