"""Step-by-step guide for Link's Awakening DX. Item requirements follow LADXR's logic."""

DUNGEONS = ["Tail Cave", "Bottle Grotto", "Key Cavern", "Angler's Tunnel",
            "Catfish's Maw", "Face Shrine", "Eagle's Tower", "Turtle Rock"]
BOSSES = ["Moldorm", "Genie", "Slime Eye", "Angler Fish", "Slime Eel", "Facade", "Evil Eagle", "Hot Head"]
ROOMS = [0x106, 0x12B, 0x15A, 0x166, 0x185, 0x1BC, 0x223, 0x234]

STEPS = {
    # ---- Pieces of Heart ------------------------------------------------------
    "hp_2a4": (
        "Get the sword so you can cut bushes.",
        "In Mabe Village, find the well and jump down it.",
        "The Piece of Heart is in the small room at the bottom.",
    ),
    "hp_2b1": (
        "Go to the fishing pond in Mabe Village and pay 10 Rupees to fish.",
        "Cast, wait for a bite, then reel in by tapping the button.",
        "Catch the big fish (the Lunker) to win the Piece of Heart.",
    ),
    "hp_044": (
        "On the Koholint Prairie, next to the Mysterious Woods, the piece sits on a patch "
        "surrounded by pits.",
        "Jump across with Roc's Feather (or find the way around) to reach it.",
    ),
    "hp_2df": (
        "Bring Bombs, Roc's Feather, and the Hookshot or Pegasus Boots.",
        "Enter the cave under the Graveyard and work through to the ledge room.",
        "Bomb your way in and cross the gaps to reach the piece.",
    ),
    "hp_2ab": (
        "Get the Power Bracelet (Bottle Grotto).",
        "In the Mysterious Woods, take the cave on the way to the Toadstool.",
        "Lift the skulls with the Power Bracelet; the piece is inside.",
    ),
    "hp_2e5": (
        "Bring Bombs and the Pegasus Boots.",
        "On the Ukuku Prairie, find the cave west of the Seashell Mansion area and bomb it open.",
        "Inside, dash with the Pegasus Boots to break through to the piece.",
    ),
    "hp_078": (
        "Get the Flippers (Angler's Tunnel).",
        "Go to Kanalet Castle and jump into its moat.",
        "Swim and dive (press B) around the moat until you pick up the piece.",
    ),
    "hp_2e6": (
        "Bring Bombs, Roc's Feather and the Hookshot.",
        "Enter the cave in the upper-right part of Animal Village's area.",
        "Bomb the wall, then jump and Hookshot across to reach the piece.",
    ),
    "hp_1e8": (
        "Beat the Lanmola in Yarna Desert.",
        "Bring Bombs and fall into the big quicksand pit.",
        "In the cave below, bomb your way to the piece.",
    ),
    "hp_1f2": (
        "Get the Flippers.",
        "Go into the Damp Cave on Tal Tal Heights.",
        "Swim through the water inside to reach the piece.",
    ),
    "hp_2ba": (
        "Bring Bombs.",
        "On Tal Tal Mountains, take the tunnel that connects the east and west sides.",
        "Bomb the cracked wall inside the tunnel; the piece is behind it.",
    ),
    "hp_000": (
        "Head to the top of the Tal Tal Mountains, near the entrance to Turtle Rock.",
        "The piece sits on the overworld there; look along the area outside the dungeon.",
    ),
    # ---- Instruments and boss Heart Containers -----------------------------------
    **{f"in_{i + 1}": (
        f"Go into {DUNGEONS[i]} (Level {i + 1}).",
        f"Find the Nightmare Key and beat {BOSSES[i]}.",
        "The instrument is in the room behind the boss.",
    ) for i in range(8)},
    **{f"hc_{ROOMS[i]:03x}": (
        f"Beat {BOSSES[i]} at the end of {DUNGEONS[i]} (Level {i + 1}).",
        "Pick up the Heart Container it leaves behind before you take the instrument.",
    ) for i in range(8)},
    # ---- Songs --------------------------------------------------------------------
    "so_ballad": (
        "Get the Ocarina from the Dream Shrine in Mabe Village.",
        "Find Marin singing by the weathercock in Mabe Village and talk to her.",
        "She teaches you the Ballad of the Wind Fish.",
    ),
    "so_mambo": (
        "Get the Ocarina and the Flippers.",
        "On Tal Tal Heights, enter the cave with the pond and swim to Manbo.",
        "Talk to him to learn Manbo's Mambo.",
    ),
    "so_frog": (
        "Bring the Ocarina and 300 Rupees.",
        "Go through the Signpost Maze on the Ukuku Prairie to Mamu's cave.",
        "Pay Mamu to learn the Frog's Song of Soul.",
    ),
    # ---- Items -------------------------------------------------------------------
    "it_sword": ("Get the shield from Tarin at the start.", "Walk along Toronbo Shores; the sword is washed up on the beach."),
    "it_shield": ("Talk to Tarin in his and Marin's house at the start of the game.",),
    "it_bracelet": ("It's the main item of Bottle Grotto (Level 2).",),
    "it_02": ("Buy bombs at the Mabe Village shop once they're in stock.",),
    "it_05": ("Save up 980 Rupees.", "Buy the Bow at the Mabe Village shop."),
    "it_06": ("It's the main item of Catfish's Maw (Level 5).",),
    "it_07": ("It's the main item of Turtle Rock (Level 8).",),
    "it_08": ("It's the main item of Key Cavern (Level 3).",),
    "it_09": ("Go into the Dream Shrine in Mabe Village.", "Make your way to the bed in the back to find the Ocarina."),
    "it_0a": ("It's the main item of Tail Cave (Level 1).",),
    "it_0b": ("Save up 200 Rupees.", "Buy the Shovel at the Mabe Village shop."),
    "it_0c": (
        "Find the Sleepy Toadstool in the Mysterious Woods (lift the obstacles with the Power Bracelet).",
        "Bring it to the Witch's hut on the Koholint Prairie.",
        "She makes Magic Powder out of it.",
    ),
    "it_0d": (
        "Bring Bombs and an item you can spare, like the Shovel.",
        "Bomb your way into the cave on Toronbo Shores and talk to the man inside.",
        "Trade him your item for the Boomerang (you can trade back later).",
    ),
    "it_flippers": ("It's the main item of Angler's Tunnel (Level 4).",),
    # ---- Upgrades ----------------------------------------------------------------
    "up_sword2": (
        "Collect 20 Secret Seashells.",
        "Go to the Seashell Mansion on the Ukuku Prairie.",
        "Watch the counter fill up; you get the L-2 Sword.",
    ),
    "up_shield2": ("It's the main item of Eagle's Tower (Level 7).",),
    "up_bracelet2": ("It's the main item of Face Shrine (Level 6).",),
    "up_powder": (
        "Get Magic Powder.",
        "Find one of the three Mad Batters (Mysterious Woods, Martha's Bay, Tal Tal Mountains).",
        "Sprinkle powder on its pot. Each batter upgrades one of Magic Powder, Bombs or Arrows, "
        "so visit all three to get all three.",
    ),
    "up_bombs": (
        "Get Magic Powder.",
        "Find one of the three Mad Batters (Mysterious Woods, Martha's Bay, Tal Tal Mountains).",
        "Sprinkle powder on its pot. Each batter upgrades one of Magic Powder, Bombs or Arrows, "
        "so visit all three to get all three.",
    ),
    "up_arrows": (
        "Get Magic Powder.",
        "Find one of the three Mad Batters (Mysterious Woods, Martha's Bay, Tal Tal Mountains).",
        "Sprinkle powder on its pot. Each batter upgrades one of Magic Powder, Bombs or Arrows, "
        "so visit all three to get all three.",
    ),
    # ---- Quest -------------------------------------------------------------------
    "qu_leaves": (
        "Get into Kanalet Castle's grounds.",
        "Leaf 1: beat the Mad Bomber hiding in the holes in the courtyard.",
        "Leaf 2: throw a rock at the crow in the tree (Power Bracelet).",
        "Leaves 3-5: inside the castle, beat the Moblins and Zols, bomb the cracked wall to reach "
        "the Darknut, and beat the ball-and-chain soldier.",
        "Bring all five to Richard in his villa to get the Slime Key.",
    ),
    "qu_trade": (
        "Win the Yoshi Doll at the Trendy Game in Mabe Village.",
        "Yoshi Doll → mother of the quadruplets (Ribbon) → CiaoCiao the dog (Dog Food) → Sale on "
        "Toronbo Shores (Bananas) → Kiki the monkey (Stick) → Tarin at the beehive (Honeycomb).",
        "Honeycomb → Chef Bear in Animal Village (Pineapple) → Papahl on the mountain (Hibiscus) → "
        "the goat in Animal Village (Letter) → Mr. Write (Broom) → Grandma Ulrira (Fishing Hook).",
        "Fishing Hook → the fisherman under the bridge (Necklace) → the mermaid (Scale) → the "
        "mermaid statue (Magnifying Lens).",
    ),
    "qu_tunic": (
        "In the Graveyard, push the gravestones in the order the book in the Library hints at to "
        "open the Color Dungeon (DX only).",
        "Solve the color puzzles and beat the boss.",
        "The Great Fairy at the end lets you choose the red tunic (attack) or blue tunic (defense).",
    ),
    # ---- Hidden seashells ---------------------------------------------------------
    "sh_0a3": ("Cut the bushes below the shop in Mabe Village.",),
    "sh_2b2": ("Bring the Shovel.", "Dig inside the dog house in Mabe Village (Bow-Wow's kennel)."),
    "sh_0d2": ("Get the Pegasus Boots.", "Dash into the tree next to Tail Cave's entrance."),
    "sh_074": ("Bring the Shovel.", "Dig next to the cave by the ghost's grave on the Koholint Prairie."),
    "sh_0a5": ("Bring the Shovel.", "Dig on the ledge above Key Cavern's entrance."),
    "sh_0a6": ("Get the Flippers.", "Swim to the little island next to Key Cavern and cut the bush."),
    "sh_08b": ("Cut the bush just east of the Seashell Mansion.",),
    "sh_0a4": ("Get the Pegasus Boots.", "Dash into the tree next to the phone booth east of Mabe Village."),
    "sh_0b9": ("Get the Power Bracelet.", "Lift the rock on the Donut Plains screen; the shell is under it."),
    "sh_0a8": ("Bring the Shovel.", "Dig next to the owl statue on the Donut Plains ledge."),
    "sh_0e9": ("Cut the lone bush on the same screen as the mermaid statue in Martha's Bay.",),
    "sh_0f8": ("Get the Flippers.", "Swim to the tiny island in Martha's Bay and cut its bush."),
    "sh_0da": ("Bring the Shovel.", "Dig next to the owl statue by the water on the peninsula."),
    "sh_1e3": ("Get the Power Bracelet.", "In the ghost's house by Martha's Bay, lift the pot inside."),
    "sh_0ff": ("Get the Power Bracelet.", "Lift the rock in the bottom-right corner of Yarna Desert."),
    "sh_00c": (
        "Get Roc's Feather and the Power Bracelet.",
        "Right of the rooster's house on Tal Tal Mountains, jump the hole in the bridge and lift the rock.",
    ),
}

SECTIONS = {
    "photos": (
        "The Camera Shop is in the Mabe Village area (DX only). Visit it once to meet the mouse.",
        "After that, the photographer mouse pops up at certain moments around the island and "
        "takes a picture.",
        "There are 12 in all. Look at the album in the Camera Shop to see which ones you still need.",
    ),
}
