"""Step-by-step instructions for every Piece of Heart in Ocarina of Time 3D."""

STEPS: dict[str, tuple[str, ...]] = {
    # ---- Kokiri Forest & Lost Woods -----------------------------------------
    "lw_skull_kid": (
        "Learn Saria's Song from Saria in the Sacred Forest Meadow (child).",
        "In the Lost Woods, take the first path on the right from the Kokiri Forest entrance.",
        "Stand on the tree stump in front of the Skull Kid and play Saria's Song.",
    ),
    "lw_memory_game": (
        "As a child with the Fairy Ocarina, find the clearing in the Lost Woods where two "
        "Skull Kids stand on stumps with a third stump between them.",
        "Stand on the middle stump and talk to them to start the memory game.",
        "Repeat each tune they play. The song gets one note longer each round.",
        "Copy the whole song without a mistake to win the piece.",
    ),
    # ---- Hyrule Field & Market ----------------------------------------------
    "hf_tektite_grotto": (
        "As an adult, go to the part of Hyrule Field near the entrance to Gerudo Valley.",
        "Find the hidden grotto there (the Stone of Agony rumbles over it) and bomb the spot open.",
        "Inside, defeat the Tektites, then sink to the bottom of the deep water with the Iron "
        "Boots, or dive with the Golden Scale.",
    ),
    "hf_scrub_grotto": (
        "In the south of Hyrule Field near the path to Lake Hylia, look for the hidden grotto "
        "inside the ring of fence posts and bushes.",
        "Bomb or Hammer it open and drop in.",
        "Throw a Deku Nut at the Business Scrub, or deflect his shot back at him, then buy the "
        "piece for 10 Rupees.",
    ),
    "mk_treasure_game": (
        "As a child, go to the Treasure Chest Shop in the Market at night (it's only open then).",
        "Pay 10 Rupees. Each room has two chests: open one, and if it holds a key, go through "
        "the door to the next room.",
        "The Lens of Truth shows you which chest has the key.",
        "The chest in the last room holds the Piece of Heart.",
    ),
    "mk_bombchu_bowling": (
        "As a child, go to the Bombchu Bowling Alley in the Market (it opens once you have bombs).",
        "Look at the prize on display before you play. It changes after every win.",
        "Win a round when the prize is the Piece of Heart.",
    ),
    "mk_lost_dog": (
        "As a child, enter the Market at night.",
        "In the back alley, find Richard: the small dog that follows you.",
        "Walk him to the house on the right in the back alley and hand him over to win the piece.",
    ),
    # ---- Lon Lon Ranch ------------------------------------------------------
    "llr_tower": (
        "As a child, go into the silo (the tall building) at Lon Lon Ranch.",
        "Move into the stacks of crates on the floor and crawl through the small gap between them.",
        "The Piece of Heart is behind the crates.",
    ),
    # ---- Kakariko & Graveyard -----------------------------------------------
    "kak_impa_house": (
        "Climb the ladder by the house under construction in Kakariko and get onto the rooftops.",
        "Jump across to the back of Impa's house, where there's an opening into the cow pen.",
        "Drop in. The Piece of Heart is in the pen with the cow.",
    ),
    "kak_windmill": (
        "Go into the Kakariko windmill.",
        "Ride the turning platforms up and jump to the ledge where the Piece of Heart sits.",
        "As a child you can also grab it with the Boomerang from the platform.",
    ),
    "kak_man_on_roof": (
        "A man sits on the roof of Impa's house in Kakariko.",
        "As a child, climb the watchtower and jump onto the roof. As an adult, Hookshot up "
        "or jump over from the ledge near the house under construction.",
        "Talk to him to get the piece.",
    ),
    "kak_50_skulltulas": (
        "Collect 50 Gold Skulltula tokens.",
        "Visit the House of Skulltula in Kakariko and talk to the cursed family member.",
    ),
    "gy_redead_grave": (
        "In the Graveyard, find the grave you can pull back that drops you into a room with "
        "Redeads (child at night, or any time as an adult).",
        "Learn the Sun's Song from the Royal Family's Tomb first.",
        "Inside, play the Sun's Song to freeze the Redeads and make a chest appear.",
        "Open the chest for the piece.",
    ),
    "gy_dampe_race": (
        "As an adult, enter Dampé's grave (the big one at the back of the Graveyard) and race "
        "his ghost through the tunnel. The first win gives the Hookshot.",
        "Race him again and reach the end in under one minute.",
        "The Piece of Heart appears at the end of the course, inside the windmill.",
    ),
    "gy_ledge": (
        "The piece is in a crate on a high ledge on the right side of the Graveyard.",
        "As a child, plant a Magic Bean in the soft soil nearby, then come back as an adult and "
        "ride the leaf platform up. The Longshot can also get you there.",
        "Break the crate to find the piece.",
    ),
    "gy_dampe_dig": (
        "As a child, go to the Graveyard at night and talk to Dampé the gravekeeper.",
        "Pay 10 Rupees for his gravedigging tour, then point him at a soft patch of soil.",
        "What he digs up is random. Keep paying until he finds the Piece of Heart.",
    ),
    # ---- Death Mountain -----------------------------------------------------
    "dmt_above_cavern": (
        "On Death Mountain Trail, find the entrance to Dodongo's Cavern.",
        "The piece sits in a nook on top of the cavern's entrance.",
        "Drop down onto it from the path above.",
    ),
    "gc_spinning_pot": (
        "As a child, go to the bottom floor of Goron City.",
        "Light all the torches there with a lit Deku Stick to start the big pot spinning.",
        "Throw a bomb into the pot when it shows the happy face to win the piece.",
    ),
    "dmc_wall": (
        "Enter Death Mountain Crater from the top of Death Mountain Trail.",
        "Climb down the wall to the left of the entrance.",
        "The piece is in an alcove in the crater wall.",
    ),
    "dmc_volcano": (
        "As a child, plant a Magic Bean in the soft soil near the Bolero of Fire warp pad in the "
        "crater (get there with Bolero of Fire, or come in from Goron City).",
        "Come back as an adult and ride the bean plant to the top of the volcano.",
        "Jump off onto the volcano for the piece.",
    ),
    # ---- Zora's River, Domain & Fountain ------------------------------------
    "zr_frogs_storms": (
        "Learn the Song of Storms in the Kakariko windmill (adult), then go back to being a child.",
        "Stand on the log in Zora's River near the frogs and play the Song of Storms.",
    ),
    "zr_frogs_game": (
        "As a child, stand on the log near the frogs in Zora's River.",
        "Play Zelda's Lullaby, Epona's Song, Saria's Song, the Sun's Song and the Song of Time "
        "for them.",
        "Then play their game: hit each note as the frog that lights up jumps.",
        "Win the game for the piece.",
    ),
    "zr_near_grotto": (
        "The piece sits on top of a tall rock pillar near the start of Zora's River.",
        "As an adult, jump across the rocks to reach it. The Hover Boots make it easy.",
    ),
    "zr_near_domain": (
        "Go to the end of Zora's River, near the waterfall to Zora's Domain.",
        "The piece is on a ledge high up across the river.",
        "Jump to it from the higher path. The Hover Boots help as an adult.",
    ),
    "zd_torches": (
        "As a child, go to Zora's Domain.",
        "Light a Deku Stick at one torch and run to light all the others before they go out "
        "(Din's Fire makes this easier).",
        "A chest appears with the piece.",
    ),
    "zf_iceberg": (
        "As an adult, go to Zora's Fountain, which is frozen over.",
        "Jump across the floating ice to the iceberg with the piece.",
    ),
    "zf_bottom": (
        "As an adult, put on the Iron Boots (and the Zora Tunic) in Zora's Fountain.",
        "Sink to the bottom of the fountain and search the floor for the piece.",
    ),
    # ---- Lake Hylia ---------------------------------------------------------
    "lh_lab_roof": (
        "As a child, plant a Magic Bean in the soft soil next to the Lakeside Laboratory.",
        "Come back as an adult after the Water Temple has refilled the lake.",
        "Ride the bean plant up and jump onto the lab's roof for the piece.",
    ),
    "lh_lab_dive": (
        "As an adult, get the Golden Scale (catch a big fish at the Fishing Pond).",
        "Go into the Lakeside Laboratory and dive to the bottom of its pool.",
        "Talk to the scientist when you surface to get the piece.",
    ),
    "lh_child_fishing": (
        "As a child, go to the Fishing Pond at Lake Hylia and pay to fish.",
        "Catch a fish that weighs 10 pounds or more and show it to the owner.",
    ),
    # ---- Gerudo Valley & Desert ---------------------------------------------
    "gv_waterfall": (
        "In Gerudo Valley, go to the edge of the cliff before the bridge.",
        "Drop down onto the ledge partway down the waterfall where the piece sits.",
        "If you fall into the river, it carries you to Lake Hylia.",
    ),
    "gv_crate": (
        "As a child, jump into the river in Gerudo Valley so it carries you to the bottom.",
        "Break the crate on the riverbank there for the piece.",
    ),
    "gf_rooftop_chest": (
        "As an adult, climb to the top of Gerudo's Fortress.",
        "From the highest roof, use the Longshot or Hover Boots to reach the separate rooftop "
        "with the chest.",
        "Open the chest for the piece.",
    ),
    "gf_archery_1000": (
        "As an adult, rescue the carpenters to get the Gerudo's Card, then ride Epona to the "
        "fortress.",
        "Pay for the horseback archery range and hit targets and pots while riding.",
        "Score 1,000 points or more for the piece.",
    ),
    "colossus_ledge": (
        "As a child, warp to the Desert Colossus with the Requiem of Spirit.",
        "Plant a Magic Bean in the soft soil there.",
        "Come back as an adult and ride the bean plant up to the ledge with the piece.",
    ),
    # ---- Dungeons -----------------------------------------------------------
    "ice_cavern": (
        "As an adult, go into the Ice Cavern from Zora's Fountain.",
        "Find the piece encased in red ice.",
        "Catch Blue Fire in a bottle and pour it on the ice to melt it.",
    ),
}
