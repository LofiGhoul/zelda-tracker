"""Step-by-step guide for Oracle of Seasons. Item locations from oracles-randomizer-ng's vanilla slot data."""

DUNGEONS = ["Gnarled Root Dungeon", "Snake's Remains", "Poison Moth's Lair", "Dancing Dragon Dungeon",
            "Unicorn's Cave", "Ancient Ruins", "Explorer's Crypt", "Sword & Shield Maze"]
BOSSES = ["Aquamentus", "Dodongo", "Mothula", "Gohma", "Digdogger", "Manhandla", "Gleeok", "Medusa Head"]


def dungeon_item(n: int, where: str = "") -> tuple[str, ...]:
    return (f"Go into {DUNGEONS[n - 1]} (Level {n}).",
            f"It's in the {where}." if where else "It's the dungeon's main item, found partway through.")


STEPS = {
    "hp_moblin_keep": ("Go to Moblin's Keep in the Natzu region.", "Open the chest inside for the piece."),
    "hp_eyeglass_cave": ("Set the season to summer at Eyeglass Lake so it dries up (Rod of Seasons).",
                         "Enter the cave on the east side of the dried lake.", "Open the chest inside."),
    "hp_subrosia_market": ("Collect Ore Chunks in Subrosia (digging, enemies, the Subrosian games).",
                           "Trade them for the Piece of Heart at the Subrosia Market."),
    "hp_maple": ("Kill enemies until Maple flies by on her broom (about every 30 kills).",
                 "Bump into her; she drops items. The Piece of Heart is one of them, usually on a later meeting.",
                 "Pick it up before she grabs it back."),
    "hp_gasha": ("Plant Gasha Seeds in soft soil around Holodrum.", "Kill enemies until each tree grows, then cut the Gasha Nut.",
                 "One nut gives a Piece of Heart (more likely once the tree has matured a lot)."),
    **{f"hc_{i}": (f"Beat {BOSSES[i - 1]} at the end of {DUNGEONS[i - 1]} (Level {i}).",
                   "Pick up the Heart Container before taking the essence.") for i in range(1, 9)},
    **{f"es_{i}": (f"Go into {DUNGEONS[i - 1]} (Level {i}).", f"Get the boss key and beat {BOSSES[i - 1]}.",
                   "The essence is in the room behind the boss.") for i in range(1, 9)},
    "it_sword": ("Go into the Hero's Cave next to where you start.", "The Wooden Sword is in the chest at the end."),
    "it_shield": ("Buy it at the Horon Village shop for 30 Rupees.",),
    "it_bombs": ("Pick them up in the early dungeons or buy them.",),
    "it_satchel": dungeon_item(1, "basement"),
    "it_ember": ("Get the Seed Satchel.", "Cut the seed tree in Horon Village."),
    "it_scent": ("Get the Seed Satchel.", "Cut the seed tree in North Horon."),
    "it_pegasus": ("Get the Seed Satchel.", "Cut the seed tree in Spool Swamp."),
    "it_gale": ("Get the Seed Satchel.", "Cut the seed tree in Sunken City (or the one in Tarm Ruins)."),
    "it_mystery": ("Get the Seed Satchel.", "Cut the seed tree in the Woods of Winter."),
    "it_bracelet": dungeon_item(2, "chest guarded by Moblins"),
    "it_shovel": ("Go to Holly's house in winter (north of Horon).", "Holly gives you the Shovel to clear the snow."),
    "it_feather": dungeon_item(3, "room with the Mimics"),
    "it_flute": ("Buy the animal flute at the Horon Village shop (150 Rupees), or get it from your animal companion.",
                 "Which animal you get (Ricky, Dimitri or Moosh) depends on how you handle the Natzu region."),
    "it_ringbox": ("Visit Vasu's ring shop in Horon Village.", "He gives you the Ring Box and the Friendship Ring."),
    "it_bombchus": ("They show up later in the game, in chests and shops.",),
    "it_biggoron": ("Finish the trading sequence.", "Bring the last trade item to Biggoron on Goron Mountain."),
    "it_rod": ("Fall into the Subrosian portal at the start.", "Take the Rod of Seasons from the Temple of Seasons."),
    "it_boomerang": ("Go to the dance hall in Subrosia.", "Win the Subrosian dance to get the Boomerang."),
    "it_slingshot": dungeon_item(4, "room with the cracked floor"),
    "it_magnet": dungeon_item(5, "chest reached with the magnet ball"),
    "it_flippers": ("Win the Master Diver's challenge in Sunken City to get the Master's Plaque.",
                    "Show the plaque to the Master Diver for Zora's Flippers."),
    "up_sword2": ("Follow the season-changing path through the Lost Woods.", "The Noble Sword is at the end."),
    "up_sword3": ("The Master Sword is a linked-game reward.",),
    "up_shield2": ("Get Hard Ore from the Great Furnace in Subrosia.", "Bring it to the Subrosian smithy for the Iron Shield."),
    "up_shield3": ("The Mirror Shield is the final shield upgrade, from the linked game.",),
    "up_satchel2": ("Get the Member's Card from the Subrosia Market.", "Buy the satchel upgrade at the members-only shop in Horon."),
    "up_satchel3": ("A later satchel upgrade; look for it after the first one.",),
    "up_bombs": ("Buy the bomb upgrade at the Subrosia Market.",),
    "up_ringbox2": ("Upgrade the Ring Box later in the game (Vasu, or secrets).",),
    "up_ringbox3": ("The largest Ring Box comes from the linked game.",),
    "up_boomerang2": dungeon_item(6, "hall with the Armos"),
    "up_slingshot2": dungeon_item(8, "chest guarded by Armos"),
    "up_feather2": dungeon_item(7, "room with the spikes"),
    **{f"se_{s}": (f"Go to the Tower of {s.title()} in Subrosia.", f"Its spirit lets the Rod of Seasons call {s}.")
       for s in ("spring", "summer", "autumn", "winter")},
}

SECTIONS = {
    "hearts": ("The named pieces are read from your save.",
               "The other pieces are counted from your heart total; look for pieces in caves, "
               "behind season-locked paths and in the Subrosian games."),
    "rings": (
        "Rings come out of Gasha Nuts, chests and secrets, and show up unappraised.",
        "Take unappraised rings to Vasu's ring shop in Horon Village to appraise them.",
        "Fixed rings include: Discovery Ring (Gnarled Root Dungeon), Rang Ring L-1 (Samasa Desert chest), "
        "Blast Ring (Western Coast beach chest), Octo Ring (cave south of Mrs. Ruul), "
        "Quicksand Ring (cave north of the first dungeon), Moblin Ring (cave outside Snake's Remains), "
        "Subrosian Ring (Talon's cave on Mt. Cucco), Power Ring L-1 (Explorer's Crypt), "
        "Steadfast Ring (Sword & Shield Maze).",
        "Some rings only come from linked games, the Ring secrets, or the GBA bonus.",
    ),
}
