"""Step-by-step guides for Ocarina of Time 3D (everything besides the Pieces of Heart, which keep their
own steps). Each item points at its vanilla location from the OoT3D Randomizer's location table."""

from games.oot3d import checklist as _c

AREA = {
    "KF": "Kokiri Forest", "LW": "the Lost Woods", "SFM": "the Sacred Forest Meadow", "HF": "Hyrule Field",
    "LLR": "Lon Lon Ranch", "MK": "the Market", "ToT": "the Temple of Time", "HC": "Hyrule Castle",
    "Kak": "Kakariko Village", "GY": "the Graveyard", "DMT": "Death Mountain Trail", "GC": "Goron City",
    "DMC": "Death Mountain Crater", "ZR": "Zora's River", "ZD": "Zora's Domain", "ZF": "Zora's Fountain",
    "LH": "Lake Hylia", "GV": "Gerudo Valley", "GF": "Gerudo's Fortress", "Wasteland": "the Haunted Wasteland",
    "Colossus": "the Desert Colossus", "OGC": "outside Ganon's Castle",
}

# check id -> (where to go, what to do there)
WHERE = {
    # songs
    "s_lullaby": ("Hyrule Castle", "After meeting Zelda in the castle courtyard, Impa teaches you Zelda's Lullaby as she escorts you out."),
    "s_epona": ("Lon Lon Ranch", "As a child, talk to Malon in the corral with the Ocarina out; she teaches you Epona's Song."),
    "s_saria": ("the Sacred Forest Meadow", "Go through the Lost Woods to the meadow's end and talk to Saria on the stump."),
    "s_sun": ("the Graveyard", "Play Zelda's Lullaby on the Triforce in front of the Royal Family's Tomb (child, night), go to the end and read the wall."),
    "s_time": ("Hyrule Field", "With all three Spiritual Stones, cross the drawbridge; Zelda throws you the Ocarina of Time and teaches the song."),
    "s_storms": ("Kakariko Village", "As an adult, play the Ocarina for the man in the windmill; he teaches you the Song of Storms."),
    "s_minuet": ("the Sacred Forest Meadow", "As an adult, climb to the meadow's end past the Moblins; Sheik is waiting."),
    "s_bolero": ("Death Mountain Crater", "As an adult, enter the crater from Death Mountain Trail; Sheik appears at the bridge."),
    "s_serenade": ("the Ice Cavern", "Finish the Ice Cavern; Sheik teaches you the song after you get the Iron Boots."),
    "s_nocturne": ("Kakariko Village", "As an adult with the Forest, Fire and Water Medallions, walk into Kakariko; Sheik appears after the scene."),
    "s_requiem": ("the Desert Colossus", "Cross the Haunted Wasteland to the Colossus; Sheik teaches you the song."),
    "s_prelude": ("the Temple of Time", "As an adult with the Forest Medallion, enter the Temple of Time; Sheik is there."),
    # quest status
    "q_emerald": ("Inside the Great Deku Tree", "Beat Queen Gohma."),
    "q_ruby": ("Dodongo's Cavern", "Beat King Dodongo."),
    "q_sapphire": ("Jabu-Jabu's Belly", "Beat Barinade."),
    "q_forest": ("the Forest Temple", "Beat Phantom Ganon."),
    "q_fire": ("the Fire Temple", "Beat Volvagia."),
    "q_water": ("the Water Temple", "Beat Morpha."),
    "q_shadow": ("the Shadow Temple", "Beat Bongo Bongo."),
    "q_spirit": ("the Spirit Temple", "Beat Twinrova."),
    "q_light": ("the Temple of Time", "Pull the Master Sword; Rauru gives you the Light Medallion in the Chamber of Sages."),
    "q_agony": ("Kakariko Village", "Bring 20 Gold Skulltula tokens to the House of Skulltula."),
    "q_card": ("Gerudo's Fortress", "As an adult, rescue all four carpenters from their cells; a Gerudo gives you the card."),
    # items
    "i_slingshot": ("Inside the Great Deku Tree", "Open the chest on the side of the second floor (the Fairy Slingshot)."),
    "i_boomerang": ("Jabu-Jabu's Belly", "Open the chest in the room with the Stingers after you carry Ruto through."),
    "i_ocarina": ("Hyrule Field", "With the three Spiritual Stones, go to the castle drawbridge; Zelda throws you the Ocarina of Time."),
    "i_bombchus": ("Kakariko Village", "Get 40 Gold Skulltula tokens, or buy them at the Bombchu Shop in the Market."),
    "i_beans": ("Zora's River", "Buy a Magic Bean from the salesman near the start of the river (price goes up each time)."),
    "i_lens": ("the Bottom of the Well", "As a child, drain the well with the Song of Storms, then beat Dead Hand for the Lens of Truth."),
    "i_hookshot": ("the Graveyard", "As an adult, enter Dampé's grave and race his ghost to the end."),
    "i_longshot": ("the Water Temple", "Beat Dark Link; the Longshot is in the chest behind him."),
    "i_bow": ("the Forest Temple", "Beat the Stalfos in the room on the west side; the Fairy Bow is in the chest."),
    "i_hammer": ("the Fire Temple", "Beat Flare Dancer on the upper floors; the Megaton Hammer chest is behind it."),
    "i_fire_arrows": ("Lake Hylia", "After the Water Temple, stand on the lab island at sunrise and shoot an arrow at the sun."),
    "i_ice_arrows": ("the Gerudo Training Ground", "Open the chest at the end of the maze path."),
    "i_light_arrows": ("the Temple of Time", "With the Shadow and Spirit Medallions, enter the Temple of Time; Zelda gives you the Light Arrows."),
    "i_dins": ("Hyrule Castle", "As a child, bomb the boulder near the castle, enter the fountain and play Zelda's Lullaby."),
    "i_farores": ("Zora's Fountain", "As a child, bomb the wall behind the rocks to reach the Great Fairy, then play Zelda's Lullaby."),
    "i_nayrus": ("the Desert Colossus", "As a child, bomb the wall by the Colossus to reach the Great Fairy, then play Zelda's Lullaby."),
    "i_bombs": ("Dodongo's Cavern", "Open the chest on the upper level (Bomb Bag)."),
    "i_sticks": ("Kokiri Forest", "Break Deku Babas for sticks, or buy them at the Kokiri Shop."),
    "i_nuts": ("Kokiri Forest", "Defeat Deku Scrubs or break pots for nuts, or buy them at the Kokiri Shop."),
    # equipment
    "e_kokiri_sword": ("Kokiri Forest", "Crawl through the hole in the training area, dodge the boulder and open the chest."),
    "e_master_sword": ("the Temple of Time", "Open the Door of Time with the three stones and the Ocarina, then pull the sword."),
    "e_biggoron_sword": ("Death Mountain Trail", "Finish the adult trading sequence and give Biggoron the Claim Check."),
    "e_deku_shield": ("Kokiri Forest", "Buy it at the Kokiri Shop (40 Rupees); also found in some dungeon chests."),
    "e_hylian_shield": ("the Graveyard", "As a child at night, pull back the grave with the flowers in front and open the chest; or buy one."),
    "e_mirror_shield": ("the Spirit Temple", "As an adult, beat the Iron Knuckle on the right side; the Mirror Shield chest is outside on the Colossus hand."),
    "e_goron_tunic": ("Goron City", "As an adult, stop the rolling Goron (Link) with a bomb; he gives you the Goron Tunic."),
    "e_zora_tunic": ("Zora's Domain", "As an adult, melt King Zora's ice with Blue Fire from the Ice Cavern."),
    "e_iron_boots": ("the Ice Cavern", "Beat the White Wolfos at the end; the Iron Boots chest is there."),
    "e_hover_boots": ("the Shadow Temple", "Beat Dead Hand in the lower area; the Hover Boots are in the chest."),
    # upgrades
    "u_quiver40": ("Kakariko Village", "As an adult, win the shooting gallery with the bow."),
    "u_quiver50": ("Gerudo's Fortress", "Score 1,500 points at horseback archery on Epona."),
    "u_bombbag30": ("the Market", "Win Bombchu Bowling while the first prize is on offer."),
    "u_bombbag40": ("Goron City", "As a child, stop the rolling Goron with a bomb."),
    "u_bracelet": ("Goron City", "Play Saria's Song for Darunia; he gives you the Goron's Bracelet."),
    "u_silver_gauntlets": ("the Spirit Temple", "As a child, reach the chest outside on the Colossus hand (child side)."),
    "u_golden_gauntlets": ("Ganon's Castle", "Open the chest in the Shadow Trial."),
    "u_silver_scale": ("Zora's Domain", "As a child, win the diving game at the top of the waterfall."),
    "u_gold_scale": ("Lake Hylia", "As an adult, catch a big enough fish at the Fishing Pond."),
    "u_wallet200": ("Kakariko Village", "Bring 10 Gold Skulltula tokens to the House of Skulltula."),
    "u_wallet500": ("Kakariko Village", "Bring 30 Gold Skulltula tokens to the House of Skulltula."),
    "u_seeds40": ("the Market", "As a child, win the shooting gallery (or hit the Lost Woods target first)."),
    "u_seeds50": ("the Lost Woods", "As a child, hit the target in the woods with the slingshot (or win the Market gallery second)."),
    "u_sticks20": ("the Lost Woods", "Show the Skull Mask at the Deku Theater (or buy it from the scrub near the bridge)."),
    "u_sticks30": ("the Lost Woods", "Whichever stick upgrade you haven't done: Deku Theater (Skull Mask) or the bridge scrub."),
    "u_nuts30": ("the Lost Woods", "Show the Mask of Truth at the Deku Theater (or buy it from the grotto scrub)."),
    "u_nuts40": ("the Lost Woods", "Whichever nut upgrade you haven't done: Deku Theater (Mask of Truth) or the grotto scrub."),
    "u_magic": ("Death Mountain Trail", "Bomb the wall at the summit to reach the Great Fairy, then play Zelda's Lullaby."),
    "u_double_magic": ("Death Mountain Crater", "As an adult, hammer the rock near the entrance and play Zelda's Lullaby in the fountain."),
    "u_double_defense": ("outside Ganon's Castle", "As an adult, lift the big rock with the Golden Gauntlets and play Zelda's Lullaby."),
    # bottles
    "b_1": ("Lon Lon Ranch", "As a child, win Talon's cucco game in the ranch house."),
    "b_2": ("Kakariko Village", "As a child, catch all seven loose cuccos and put them back in the pen."),
    "b_3": ("Lake Hylia", "As a child with the Silver Scale, dive to the bottom of the lake near the lab for Ruto's Letter."),
    "b_4": ("the Market", "As an adult, sell 10 Big Poes (from Hyrule Field) to the Poe Collector in the guard house."),
    # heart containers
    "r_gohma": ("Inside the Great Deku Tree", "Beat Queen Gohma and pick up the Heart Container."),
    "r_king_dodongo": ("Dodongo's Cavern", "Beat King Dodongo and pick up the Heart Container."),
    "r_barinade": ("Jabu-Jabu's Belly", "Beat Barinade and pick up the Heart Container."),
    "r_phantom_ganon": ("the Forest Temple", "Beat Phantom Ganon and pick up the Heart Container."),
    "r_volvagia": ("the Fire Temple", "Beat Volvagia and pick up the Heart Container."),
    "r_morpha": ("the Water Temple", "Beat Morpha and pick up the Heart Container."),
    "r_bongo_bongo": ("the Shadow Temple", "Beat Bongo Bongo and pick up the Heart Container."),
    "r_twinrova": ("the Spirit Temple", "Beat Twinrova and pick up the Heart Container."),
}

STEPS = {cid: (f"Go to {where}." if not where.startswith("Inside") else f"Go {where[0].lower() + where[1:]}.", what)
         for cid, (where, what) in WHERE.items()}

# Gold Skulltulas: area, the hint, and how to collect
for gs in _c.gold_skulltulas(False) + _c.gold_skulltulas(True):
    if gs.id not in STEPS:
        lines = [f"Go to {gs.group}."]
        lines.append(gs.hint if gs.hint else f"It's in the '{gs.name}' part of the dungeon.")
        lines.append("Listen for the clicking, kill it (sword, Boomerang or Hookshot) and grab the token.")
        STEPS[gs.id] = tuple(lines)

SECTIONS = {
    "gold_skulltulas": (
        "Gold Skulltulas make a clicking sound when you're near. Most overworld ones only come out at night.",
        "Kill them with the sword, Boomerang or Hookshot, then grab the token.",
        "Soft-soil ones: drop bugs from a bottle onto the soil patch as a child.",
        "Tree ones: roll into the tree as a child.",
        "Turn in tokens at the House of Skulltula in Kakariko for rewards.",
    ),
    "skulltula_house": ("Go to the House of Skulltula in Kakariko Village.", "Talk to the family member for each reward once you have enough tokens."),
}
