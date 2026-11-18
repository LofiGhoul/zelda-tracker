"""Step-by-step guide for A Link Between Worlds."""

RAVIO_ITEM = ("Go to Ravio's shop in Link's house.", "Rent or buy the item; only buying it counts as owning it.",
              "Bought items stay with you even if you lose a fight.")
NICE = ("Buy the item from Ravio first (rented items can't be upgraded).",
        "Rescue Maiamai around Hyrule and Lorule (100 in all, hiding under rocks, in trees and on walls).",
        "Bring 10 Maiamai to Mother Maiamai at Lake Hylia per upgrade and pick this item.")

STEPS = {
    "pe_courage": ("Go to the Eastern Palace east of Kakariko.", "Beat the boss at the top for the Pendant of Courage."),
    "pe_power": ("Go to the House of Gales on Lake Hylia's island.", "Beat Margomill for the Pendant of Power."),
    "pe_wisdom": ("Climb Death Mountain to the Tower of Hera.", "Beat Moldorm for the Pendant of Wisdom."),
    **{f"rv_{off:x}": RAVIO_ITEM for off in (0xCC, 0xCB, 0xD3, 0xCA, 0xD0, 0xD1, 0xD2, 0xCF, 0xCE)},
    **{f"ni_{off:x}": NICE for off in (0xCC, 0xCB, 0xD3, 0xCA, 0xD0, 0xD1, 0xD2, 0xCF, 0xCE)},
    "it_e9": ("Catch bees for the Bee Guy in Kakariko Village.", "He gives you the Bee Badge."),
}

SECTIONS = {
    "hearts": (
        "10 hearts come from the dungeon bosses.",
        "The other 7 come from 28 Pieces of Heart (4 per heart), hidden in both Hyrule and Lorule, "
        "in caves, minigames and behind wall-merging paths.",
        "The save only shows your total here, so the list fills in as your hearts go up.",
    ),
    "bottles": (
        "There are 5 bottles, from side quests, minigames and shops in Hyrule and Lorule.",
    ),
    "items": (
        "Most of these are story items or quest rewards in Hyrule and Lorule.",
        "Titan's Mitt is the upgrade to the Power Glove.",
    ),
}
