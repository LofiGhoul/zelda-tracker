"""Step-by-step guide for Twilight Princess (GameCube). Locations and requirements come from the
Twilight Princess Randomizer's check data (games/guides/tp_data.py)."""

from .tp_data import BUG_SPOTS, HEART_PIECE_STEPS

BUGS = ["Beetle", "Butterfly", "Stag Beetle", "Grasshopper", "Phasmid", "Pill Bug",
        "Mantis", "Ladybug", "Snail", "Dragonfly", "Ant", "Dayfly"]


def _bug_steps(i: int) -> tuple[str, ...]:
    sex = "Male" if i % 2 == 0 else "Female"
    name = BUGS[i // 2]
    spot = BUG_SPOTS.get(f"{sex}_{name.replace(' ', '_')}")
    if not spot:
        return ()
    where, area, need = spot
    out = [f"Go to {area}.", f"The {sex.lower()} {name} is at {where}; look for the golden glow and listen for its buzz."]
    if need:
        out.append(need)
    out.append("Catch it, then show it to Agitha in her house in Castle Town.")
    return tuple(out)

BUG_GUIDE = ("Golden Bugs hide all over Hyrule; each kind comes as a male and a female.",
             "Catch it (Gale Boomerang, Clawshot or just walk up to it), then show it to Agitha in her house in Castle Town.",
             "Agitha rewards you with Rupees and, at milestones, the Big and Giant Wallets.")

STEPS = {
    **HEART_PIECE_STEPS,
    **{f"bg_{i}": _bug_steps(i) for i in range(24)},
    **{f"hc_{i + 1}": (f"Go into {d}.", f"Beat {b} at the end.", "Pick up the Heart Container it leaves behind.")
       for i, (d, b) in enumerate((("the Forest Temple", "Diababa"), ("the Goron Mines", "Fyrus"),
                                   ("the Lakebed Temple", "Morpheel"), ("the Arbiter's Grounds", "Stallord"),
                                   ("Snowpeak Ruins", "Blizzeta"), ("the Temple of Time", "Armogohma"),
                                   ("the City in the Sky", "Argorok"), ("the Palace of Twilight", "Zant")))},
    "fs_1": ("Go into the Forest Temple in Faron Woods.", "Beat Diababa for the first Fused Shadow."),
    "fs_2": ("Go into the Goron Mines on Death Mountain.", "Beat Fyrus for the second Fused Shadow."),
    "fs_3": ("Go into the Lakebed Temple under Lake Hylia (needs the Zora Armor).", "Beat Morpheel for the third Fused Shadow."),
    "ms_1": ("Go into the Arbiter's Grounds in the Gerudo Desert.", "Beat Stallord; the Mirror of Twilight is revealed and you get the first shard."),
    "ms_2": ("Go into Snowpeak Ruins.", "Beat Blizzeta for the second Mirror Shard."),
    "ms_3": ("Go into the Temple of Time beyond the Sacred Grove.", "Beat Armogohma for the third Mirror Shard."),
    "ms_4": ("Go into the City in the Sky (fire yourself up with the Lake Hylia cannon).", "Beat Argorok for the last Mirror Shard."),
    "it_4b": ("Save up 30 Rupees.", "Buy the Slingshot at Sera's shop in Ordon Village."),
    "it_48": ("Talk to Coro in his house in Faron Woods.", "He gives you the Lantern."),
    "it_40": ("It's the main item of the Forest Temple, after the Ook fight.",),
    "it_45": ("Go to Bo's house in Ordon Village.", "Beat him in a sumo match to get the Iron Boots."),
    "it_43": ("Go into the Goron Mines.", "Beat Dangoro (needs the Iron Boots); the Hero's Bow is in the chest after him."),
    "it_3e": ("Buy the Hawkeye at the Malo Mart in Kakariko Village.",),
    "it_50": ("Finish the Goron Mines.", "Buy a bomb bag from Barnes in Kakariko Village when his shop reopens.",
              "Iza in Upper Zora's River gives another bag (Helping Hand), and the Giant Bomb Bag for her rapids game; "
              "a Goron underwater in Zora's Domain has the last one (Water Bombs and Iron Boots)."),
    "it_44": ("Go into the Lakebed Temple (Zora Armor).", "Beat the Deku Toad; the Clawshot is in its chest."),
    "it_41": ("Go into the Arbiter's Grounds.", "Beat the Death Sword; the Spinner is in its chest."),
    "it_42": ("Go into Snowpeak Ruins.", "Beat Darkhammer for the Ball and Chain."),
    "it_46": ("Go into the Temple of Time.", "Beat the Darknut for the Dominion Rod."),
    "it_47": ("Go into the City in the Sky.", "Beat the Aeralfos for the second Clawshot."),
    "it_4a": ("Find Uli's cradle (the monkey takes it in Faron Woods) and bring it back to her in Ordon.",
              "She gives you the Fishing Rod."),
    "it_84": ("Help Ilia get her memory back.", "She gives you the Horse Call."),
    "it_28": ("Early on, Rusl gives you a wooden sword as a gift.",
              "Later, after Faron's twilight, take the Ordon Sword from Rusl's house in Ordon Village."),
    "it_29": ("Go through the Sacred Grove in Faron Woods.", "Pull the Master Sword from its pedestal."),
    "it_49": ("Beat the Palace of Twilight.", "The Master Sword is filled with light."),
    "it_2a": ("Buy the Wooden Shield at the Malo Mart in Kakariko Village.",),
    "it_2c": ("Buy the Hylian Shield at the Malo Mart in Kakariko Village (200 Rupees).",),
    "it_31": ("After the Goron Mines, follow Rutela's ghost to the Zora graveyard in Kakariko.", "She gives you the Zora Armor."),
    "it_30": ("Save up 598 Rupees (you'll need a bigger wallet).", "Buy the Magic Armor at the Malo Mart in Castle Town."),
    "it_35": ("Find Golden Bugs and give them to Agitha in Castle Town.", "One of her rewards is the Big Wallet."),
    "it_36": ("Keep bringing Agitha Golden Bugs.", "A later reward is the Giant Wallet."),
    "it_55": ("Get the Clawshot.", "Play the STAR game in the tent in Castle Town and win the first round for the Big Quiver."),
    "it_56": ("Get the Double Clawshots.", "Win the STAR game's second, harder round for the Giant Quiver."),
}

SECTIONS = {
    "hearts": (
        "There are 45 Pieces of Heart (5 per heart); 8 more hearts come from the dungeon bosses.",
        "Each piece below has its own steps and the items you'll need for it.",
        "Your save only keeps the heart total, so the tracker can't tick off individual pieces; "
        "use the count at the top to see how many you still need.",
    ),
    "bugs": BUG_GUIDE,
    "poes": (
        "Poes only come out at night. Switch to wolf form and use your senses to see them.",
        "Defeat each Poe and pull its soul out.",
        "Bring the souls to Jovani in Castle Town; he gives rewards at 20 and 60 souls.",
    ),
    "letters": (
        "The postman delivers letters as the story moves on.",
        "Read them in your Collection screen; some come from shopkeepers and friends you've met.",
    ),
    "bottles": (
        "Bottle 1: help Sera's cat come home in Ordon; she gives you a bottle of milk.",
        "Bottle 2: buy lantern oil in a bottle from Coro in Faron Woods.",
        "Bottle 3: fish it out of the water at Hena's Fishing Hole.",
        "Bottle 4: Jovani gives one after you bring him 20 Poe Souls.",
    ),
}
