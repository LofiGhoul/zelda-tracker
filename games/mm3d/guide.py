"""Step-by-step instructions for every Piece of Heart in Majora's Mask 3D.

Keys match `Piece.id` in mm3d_save.py. Written for the 3DS version; places where
it differs from the N64 original are called out.
"""

STEPS: dict[str, tuple[str, ...]] = {
    # ---- Clock Town -----------------------------------------------------------
    "mayor": (
        "Finish the Anju & Kafei quest to get the Couple's Mask.",
        "Go to the Mayor's Residence in East Clock Town during the day and enter the meeting room "
        "where the Mayor, Mutoh and Viscen are arguing.",
        "Put on the Couple's Mask. It ends the meeting and the Mayor gives you the piece.",
    ),
    "town_gallery": (
        "Visit the Town Shooting Gallery in East Clock Town as human Link with the Hero's Bow.",
        "Score 40 or more first. That prize is the bigger quiver.",
        "Play again and get a perfect score by hitting every red Octorok. The heart piece is the perfect-score prize.",
    ),
    "honey_darling": (
        "Visit Honey & Darling's shop in East Clock Town during the day.",
        "Win their game on Day 1, Day 2 and Day 3 of the same cycle. The game changes each day.",
        "Don't play the Song of Time in between. Winning all three days earns the piece.",
    ),
    "chest_game": (
        "Put on the Goron Mask and enter the Treasure Chest Shop in East Clock Town.",
        "Pay to play and find your way through the maze to the chest before time runs out.",
        "The first win as Goron Link gives the heart piece.",
    ),
    "postbox": (
        "Get the Postman's Hat: give Kafei's Express Mail to Mama to the postman. On the Final Day "
        "he decides to flee town and gives you his hat.",
        "Wear the Postman's Hat and check any postbox in Clock Town.",
        "A heart piece is inside.",
    ),
    "keaton": (
        "Get the Keaton Mask (Kafei's partner gives it to you at the Curiosity Shop's back room on the Final Day).",
        "Wear it and find a ring of bushes with one that moves: North Clock Town, Milk Road or Mountain Village.",
        "Cut the moving bush to summon Keaton, then answer all five quiz questions correctly.",
    ),
    "deku_playground": (
        "As Deku Link, visit the Deku Scrub Playground in North Clock Town during the day.",
        "Collect every rupee faster than the record set by the Business Scrubs.",
        "Win on Day 1, Day 2 and Day 3 of the same cycle for the piece.",
    ),
    "nct_tree": (
        "In North Clock Town, climb the wooden platform beside the playground slide.",
        "Instead of sliding down, jump across onto the big tree.",
        "The piece is sitting on top of the tree.",
    ),
    "sct_platform": (
        "Get the Moon's Tear from the Astral Observatory, then give it to the Business Scrub on the "
        "Deku Flower in front of the Clock Tower (South Clock Town). You get the Land Title Deed.",
        "The scrub leaves, and his Deku Flower stays behind.",
        "As Deku Link, launch from that flower and float to the ledge above the Clock Tower door.",
    ),
    "bank": (
        "Find the bank. In MM3D it's in South Clock Town, built into the back of the Clock Tower.",
        "Keep depositing rupees. Your bank balance survives the Song of Time.",
        "When your balance reaches 5,000 rupees, the banker gives you the heart piece.",
    ),
    "postman_game": (
        "Visit the Post Office in West Clock Town on Day 1 or Day 2 in the afternoon or evening, "
        "when the postman is practicing.",
        "Play his game: press the button at exactly 10.00 seconds without a visible timer.",
        "Wearing the Bunny Hood makes the timer visible, which makes it easy.",
    ),
    "rosa": (
        "Get Kamaro's Mask: at midnight, find Kamaro dancing on a rock in north Termina Field and "
        "play the Song of Healing for him.",
        "At night, go to the Rosa Sisters in West Clock Town.",
        "Put on Kamaro's Mask and dance to teach them a new routine. They give you the piece.",
    ),
    "swordsman": (
        "Go to the Swordsman's School in West Clock Town and choose the Expert (advanced) course.",
        "Cut every log with a jump attack to score the maximum 30 points.",
        "A perfect 30 earns the heart piece.",
    ),
    "toilet_hand": (
        "Go to the Stock Pot Inn between midnight and 6 a.m. (you need the Room Key, or climb in "
        "through the upper door as Deku Link).",
        "Knock on the toilet door upstairs and a hand asks for paper.",
        "Give it a Title Deed or a letter, and it hands you the piece.",
        "Note: MM3D forgets this flag after the Song of Time, so the app infers it from your heart count.",
    ),
    "grandma_short": (
        "Get the All-Night Mask: stop Sakon from stealing the Bomb Bag on Night 1, then buy the "
        "mask at the Curiosity Shop on the Final Night.",
        "Wear it and talk to Anju's grandmother in the Stock Pot Inn.",
        "Choose the short story (the Carnival of Time) and answer that it's held on the eve of the festival.",
    ),
    "grandma_long": (
        "Wear the All-Night Mask so you stay awake for the whole story.",
        "Talk to Anju's grandmother in the Stock Pot Inn and choose the long story (the Four Giants).",
        "When she asks her question, answer \"I dunno\".",
    ),
    # ---- Termina Field & Ranch ------------------------------------------------
    "gossip_grotto": (
        "Termina Field has four grottos with gossip stones in them.",
        "In each grotto, play one transformation song as its form: Sonata of Awakening as Deku Link, "
        "Goron Lullaby as Goron Link, or New Wave Bossa Nova as Zora Link.",
        "Use the same song in all four so every stone glows the same color. A heart piece appears.",
    ),
    "tf_scrub": (
        "Look through the telescope in the Astral Observatory and spot a Business Scrub flying into a hole in Termina Field.",
        "Follow him into that grotto. He offers a heart piece for 150 rupees.",
        "Turn him down once and he drops the price to 100.",
    ),
    "bio_baba": (
        "Find the small rock on the Termina Field path toward Great Bay and blow it up (bomb or Goron punch).",
        "Drop into the grotto. Bio Deku Babas hang under the lily pads in the water.",
        "Dive as Zora Link and defeat them. One of them is holding the piece.",
    ),
    "tf_chest_a": (
        "Peahat grotto: in tall grass near the Milk Road side of Termina Field. Defeat the giant Peahat "
        "(easiest during the day) and open the chest.",
        "Dodongo grotto: under the mushroom-shaped rock in the northwest of Termina Field. Defeat both "
        "Dodongos and open the chest.",
        "The save can't tell these two apart, so they're listed as #1 and #2.",
    ),
    "tf_chest_b": (
        "Do whichever of the Peahat grotto (tall grass near Milk Road) or the Dodongo grotto (under the "
        "mushroom-shaped rock, northwest field) you haven't done yet.",
        "Defeat the enemies and open the chest for the piece.",
    ),
    "dog_race": (
        "Go to the Doggy Racetrack at Romani Ranch during the day.",
        "Wear the Mask of Truth and pick up the dogs to read their thoughts. Choose one that says it feels great.",
        "Bet on it and win at least 150 rupees in a single race to get the piece.",
    ),
    # ---- Southern Swamp & Woodfall --------------------------------------------
    "swamp_gallery": (
        "Visit the Swamp Shooting Gallery on the Road to Southern Swamp with the Hero's Bow.",
        "Earn the Largest Quiver first with a high score.",
        "Play again and get a perfect score (hit every target) for the heart piece.",
    ),
    "rss_tree": (
        "On the Road to Southern Swamp, find the vine-covered tree near where Tingle floats.",
        "Defeat the Bad Bats and climb the vines.",
        "The piece is up in the tree.",
    ),
    "swamp_scrub": (
        "Give the Land Title Deed to the Business Scrub at the Swamp Tourist Center. He trades you the Swamp Title Deed.",
        "He leaves his Deku Flower behind.",
        "As Deku Link, launch from it and float onto the Tourist Center roof for the piece.",
    ),
    "photo_contest": (
        "Get the Pictograph Box from Koume (save her in the Woods of Mystery with a red potion).",
        "Take a pictograph of the Deku King inside Deku Palace.",
        "Show it to the man at the Swamp Tourist Center counter. The best photo wins the heart piece.",
    ),
    "deku_palace": (
        "As Deku Link, enter Deku Palace and head into the west inner garden.",
        "Hop between the flowers and avoid the guards' sight. Getting spotted sends you back.",
        "The piece is at the far end of the garden.",
    ),
    "woodfall_chest": (
        "In the Woodfall area (outside the temple), go to the Deku Flower near the owl statue.",
        "As Deku Link, launch and float from flower to flower around the area.",
        "Land on the platform with the chest and open it.",
    ),
    # ---- Snowhead -------------------------------------------------------------
    "frog_choir": (
        "Get Don Gero's Mask from the Goron in Mountain Village by giving him a Rock Sirloin.",
        "Wearing the mask, talk to the four frogs: the Laundry Pool, the Southern Swamp (after Woodfall), "
        "the Woodfall Temple miniboss room and the Great Bay Temple miniboss room.",
        "After beating Goht, return to Mountain Village in spring and talk to the frogs on the pond while wearing the mask. They sing and you get the piece.",
    ),
    "goron_scrub": (
        "Give the Swamp Title Deed to the Business Scrub in Goron Village. He trades you the Mountain Title Deed.",
        "He leaves his Deku Flower behind.",
        "As Deku Link, launch from it and float to the high ledge for the piece.",
    ),
    "snowhead_path": (
        "Teach the Scarecrow a song first (the scarecrow in the Trading Post or Astral Observatory).",
        "On the Path to Snowhead, use the Lens of Truth to find hidden platforms near the big jumps.",
        "Play the Scarecrow's Song to summon him, Hookshot to him, and reach the pillar with the piece.",
    ),
    "twin_islands": (
        "Beat Goht so spring comes and the Twin Islands lake thaws.",
        "Dive as Zora Link to the bottom of the lake.",
        "Open the chest down there for the piece.",
    ),
    # ---- Great Bay ------------------------------------------------------------
    "fisherman": (
        "Clear the Great Bay Temple first.",
        "Hookshot or swim to the fisherman's island at Great Bay Coast and play his torch-jumping game.",
        "Score 20 or more points for the heart piece.",
    ),
    "lab_fish": (
        "Catch fish from the sea in empty bottles.",
        "In the Marine Research Lab, release them into the small aquarium with the big fish.",
        "After it eats enough of them (about 5 to 7), it spits out the piece.",
    ),
    "gbc_ledge": (
        "At Great Bay Coast, Hookshot up the stone pillars in the northeast.",
        "Plant a Magic Bean in the soft soil up there and water it (Song of Storms or a bottle of spring water).",
        "Ride the bean platform up, then play the Scarecrow's Song and Hookshot to the scarecrow to reach the ledge.",
    ),
    "ocean_spider_house": (
        "Wear the Captain's Hat in the Oceanside Spider House so the Stalchildren talk to you.",
        "They reveal the color order of the masks on the wall.",
        "Shoot the masks in that order with arrows to open the chest with the piece.",
    ),
    "beaver_race": (
        "Hookshot up to the top of the Waterfall Rapids at Zora Cape and challenge the beaver brothers as Zora Link.",
        "The first win gives an Empty Bottle.",
        "Race again and win the harder second race for the heart piece.",
    ),
    "zora_cape": (
        "At Zora Cape, swim as Zora Link to the area under the waterfall on the east side.",
        "A Like Like lurks underwater.",
        "Defeat it, using Zora electricity or arrows, and it drops the piece.",
    ),
    "evan": (
        "In Zora Hall, go to Mikau's room as human Link and read his diary. It contains the song he was writing.",
        "Jam with Japas as Zora Link.",
        "Play the song from the diary for Evan, the band leader, and he gives you the piece.",
    ),
    "zora_scrub": (
        "Give the Mountain Title Deed to the Business Scrub in Lulu's room in Zora Hall. He trades you the Ocean Title Deed.",
        "He leaves his Deku Flower behind.",
        "As Deku Link, launch from it and float to the high ledge for the piece.",
    ),
    "seahorse": (
        "Take a pictograph of a Gerudo pirate and give it to the fisherman at Great Bay Coast. He gives you a seahorse in a bottle.",
        "Swim as Zora Link to Pinnacle Rock and release it.",
        "Defeat all the Deep Pythons to free its partner. The reunited seahorses give you the piece.",
    ),
    "pirate_sewer": (
        "Enter Pirates' Fortress through the underwater tunnel as Zora Link.",
        "In the sewer passages, a heart piece sits inside a cage.",
        "Hit the switch nearby and get into the cage before the gate shuts.",
    ),
    # ---- Ikana ----------------------------------------------------------------
    "spirit_house": (
        "Find the Spirit House (Poe hut) in Ikana Canyon.",
        "Pay 30 rupees to fight the four Poe Sisters.",
        "Defeat all four within the time limit for the piece.",
    ),
    "ikana_scrub": (
        "Give the Ocean Title Deed to the Business Scrub in Ikana Canyon (east of the river).",
        "He leaves his Deku Flower behind.",
        "As Deku Link, launch from it and float across to the ledge with the piece.",
    ),
    "graveyard_ik": (
        "On the Second Night, wear the Captain's Hat in Ikana Graveyard and have the Stalchildren open the second grave.",
        "Go down, find the hidden path with the Lens of Truth, and blow open the cracked wall.",
        "Defeat the Iron Knuckle and open the chest for the piece.",
    ),
    "dampe": (
        "On the Third Night, talk to Dampé in his house at Ikana Graveyard and go to the basement.",
        "Lead him to the spots with ghostly flames so he digs them up.",
        "Defeat the Big Poe that appears and open the chest. In MM3D it holds a heart piece (N64 gave a bottle).",
    ),
    "ikana_castle": (
        "Reach the roof of the Ancient Castle of Ikana.",
        "Shoot the switch on the north pillar to put out the flames for a short time.",
        "Hurry to the Deku Flower and float to the pillar to grab the piece before the fire comes back.",
    ),
    "secret_shrine": (
        "Use Light Arrows to open the Secret Shrine on the west side of the Ikana Canyon river.",
        "Defeat the four mini-bosses (Dinolfos, Wizzrobe, Wart, Garo Master) in their rooms.",
        "Return to the main hall and open the final chest for the piece.",
    ),
    # ---- Moon -----------------------------------------------------------------
    "moon_deku": (
        "On the Moon, talk to the child in the Odolwa mask and give them one mask to enter the Deku trial.",
        "As Deku Link, take the Gold Deku Flower on the second spinning platform.",
        "Float to the corner ledge to grab the piece.",
    ),
    "moon_goron": (
        "Give the child in the Goht mask two masks to enter the Goron trial.",
        "Roll through the track as Goron Link.",
        "The piece is along the course. Keep your speed up to reach it.",
    ),
    "moon_zora": (
        "Give the child in the Gyorg mask three masks to enter the Zora trial.",
        "Swim through the tunnel maze as Zora Link.",
        "Explore the side branches to find the piece.",
    ),
    "moon_link": (
        "Give the child in the Twinmold mask four masks to enter the Link trial.",
        "Fight through the rooms as human Link.",
        "The piece is in the second-to-last room.",
    ),
}
