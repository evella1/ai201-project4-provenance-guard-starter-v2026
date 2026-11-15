"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

# ── The texts ────────────────────────────────────────────────────────────────
# Kept in lists so a text can serve more than one criterion without being
# copied twice. Full sources and scores for the calibration texts are in
# samples/calibration.md.

# My own writing: written by me, no AI, no grammar tool. Mixed types on
# purpose (plain, formal, instructions, essay-style, casual, story, opinion),
# because a test of only casual writing would pass too easily.
MY_WRITING = [
    # plain everyday writing
    "Today, I went to see my friend at a coffee shop. We ordered pastries and "
    "coffee. Unfortunately the coffee came with extra sugar, which I didn't ask "
    "for. I almost asked for a refund but held back seeing how busy the baristas "
    "were. We had some good chat about what we've been up to in the last few "
    "weeks. She told me she's been working out a lot. I found that inspiring and "
    "I signed up for a gym the next day. We'll see how it goes.",

    # formal: an email asking race organisers a question
    "We are a couple from California. We're currently traveling and we'll be "
    "staying in Mauritius for a few months. We're interested in joining some of "
    "the trail runs, we're specifically looking at the Avalon Race 11km. Is the "
    "medical certificate required to sign up?  Is it also required for the 4km "
    "run? We are not able to obtain it, since we have no medical history in "
    "Mauritius. We're in our 30s and do 10km runs regularly.",

    # formal: a professional email about an internship search
    "I apologize for the delayed answer. Thank you for reaching out to me and "
    "offering help with the internship search. I am currently changing careers "
    "from accounting to software development and I am actively applying for "
    "internships during this recruiting season. I have only completed one Forage "
    "virtual experience, but I am planning to attempt more programs as time "
    "allows. I have found it very informative and I believe it will be "
    "beneficial in the job search. I have attached my resume to this email. If "
    "there is any feedback you have, I would greatly appreciate it.",

    # friendly email to a former coworker (the name is changed to a placeholder)
    "Hi Anna,\n\n"
    "Hope you are doing well!\n\n"
    "I am going through recruitment for a job and I just wanted to let you know "
    "in advance that someone might be calling or emailing next week to verify my "
    "employment. It should come from ABC Wholesale.\n\n"
    "I was in Chicago in October with my mom, but just for the weekend, so "
    "unfortunately I was not able to stop by the office. I hope I will have a "
    "chance to see the team next time I visit!\n\n"
    "Thank you & all the best to you and your family in the New Year!",

    # casual work message to a manager
    "I have not been able to log on to the laptop. We are waiting for the other "
    "IT person to provide the admin password. I will keep you posted! In the "
    "meantime, could you tell me what the planned end date of my contract is? I "
    "think you mentioned Jan 31st? I am planning some things for February, so I "
    "wanted to make sure.",

    # customer service message asking about a credit
    "On the day of the reservation, it was impossible to find parking by the "
    "facility, so I was not able to use the service. I was offered a credit to "
    "be used in the future and I was told it will show under my name. I just "
    "wanted to confirm that the credit is available to use, before making the "
    "reservation.",

    # personal notes while coding a dice game (a list, almost no punctuation,
    # so the style signal sees fewer than 3 sentences and returns 0.5)
    "computer player goes first\n"
    "only check the total score after both take turns\n"
    "recalculate the total of scores in the main function\n"
    "pycharm can run a portion of code\n"
    "need to set the running game to false to break\n"
    "play again is after someone wins!\n"
    "show status after each turn (not roll)\n"
    "computer can look at the human score and roll if behind",

    # technical / essay-style: part of a written solution to a math problem
    # (line breaks from the original page layout joined; typos kept)
    "We can treat the houses as dots on a grid and apply coordinates to them for "
    "clearer visualization of the problem. Let us think about any two houses on "
    "the grid and when a drone would fly directly over some house in the very "
    "middle of the flight between the two houses. We can distinguish 3 cases "
    "when this will be true:\n"
    "Case 1: Horizonal flight: every other house on the way will match the "
    "requirement. As shown in Figure 3: for a house at (0,0) the horizontal "
    "houses that match the criteria are: (2,0), (4,0), (6,0), (8,0).\n"
    "Case 2: Vertical flight: every other house on the way will match the "
    "requirement. As shown in Figure 3: for a house at (0,0) the vertical houses "
    "that match the criteria are: (0,2), (0,4), (0,6), (0,8).\n"
    "Case 3: Diagonal flight: if the rectangle created by the diagonal that "
    "represents the flight has even number of cells on both sides. As shown in "
    "Figure 3: for a house at (0,0) the houses that match the criteria are: "
    "(2,2), (2,4), (2,6), (2,8), (4,2), (4,4), (4,6), (4,8), (6,2), (6,4), "
    "(6,6), (6,8), (8,2), (8,4), (8,6), (8,8).\n"
    "To visualize that this is true we can divide the rectangle in 4 smaller "
    "rectangles and observe that the diagonal of the smaller rectangles needs to "
    "connect their vertices and therefore the center of the larger rectangle and "
    "the center of its diagonal will be exactly at point (2,1) where a house is "
    "located. (Figure 2).",

    # academic: algorithm, proof and run-time analysis for a homework problem
    # (line breaks from the PDF layout joined; wording and typos kept)
    "Algorithm:\n"
    "Input: adjacency list representing graph G, linked list representing E′ "
    "edges, integer representing max flow in G\n"
    "Output: maximum flow in G′\n"
    "Create G′ by adding edges from E′ to G. Run Ford-Fulkerson algorithm to "
    "find the maximum flow.\n"
    "Proof of correctness:\n"
    "Because a maximum flow has already been found, when we construct a residual "
    "graph while running Ford-Fulkerson, there will be no augmenting paths that "
    "do not involve one of the new edges, as Ford-fulkerson stops where there are "
    "no more s − t paths in the residual graph. Since each of the new edges has a "
    "capacity of 1, we can say that the total capacity of the new edges is equal "
    "to the number of new edges k. As this is the most capacity we could hope to "
    "add to the existing graph, we know that the algorithm will run at most k "
    "times.\n"
    "Run-time analysis:\n"
    "Adding an edge to an adjacency list takes O(1) time. Therefore adding k "
    "edges will take O(k) time. We know that running Ford-Fulkerson on a given "
    "graph takes O(C(n + m). In our case m = |E| + |E′| because we have to run "
    "the algorithm on the new edges as well. Let us prove that C = k. C is the "
    "number of iterations, which is at most the sum of capacities of edges "
    "leaving s. It is important to note that any new augmented path found in G′ "
    "has to include one of the edges in E′ and the total of the capacity of "
    "edges in E′ = |E′| = k, sinceevery edge in E′ has a capacity of 1. "
    "Therefore C = k. The total time complexity is therefore "
    "O(k) +O(k(|V |+|E|+|E′|)) = O(k(|V |+|E|+|E′|)).",

    # casual message to a seller about seeing an item (the phone number is a
    # placeholder, not a real one)
    "I'm gonna be free tomorrow afternoon to come by see it. I'm going to text "
    "you then and see if it's still available. It might be around 4pm, I'll "
    "know an hour in advance if that's ok. Here's my number just in case "
    "1234567898. You can text me or message me on here.",
]

# AI-generated texts (not edited unless the comment says so).
AI_TEXTS = [
    # clearly AI
    "Time management is an essential skill that plays a crucial role in both "
    "academic and professional success. By prioritizing tasks effectively, "
    "individuals can reduce stress and enhance their overall productivity. One "
    "widely recommended strategy is breaking larger projects into smaller, more "
    "manageable steps, which helps prevent procrastination and fosters a sense of "
    "accomplishment. Additionally, tools such as planners and digital calendars "
    "can provide valuable structure. However, it is important to remember that "
    "effective time management is not about filling every moment with work. "
    "Rather, it involves striking a healthy balance between responsibilities and "
    "rest. In conclusion, mastering time management empowers individuals to "
    "achieve their goals while maintaining their well-being.",

    # the same essay, lightly edited by hand
    "Time management is an important skill that plays a key role in both academic "
    "and professional success. By prioritizing tasks effectively, individuals can "
    "reduce stress and improve their overall productivity. One strategy often "
    "recommended is breaking larger projects into smaller more manageable steps, "
    "which helps prevent procrastination and gives a sense of accomplishment. "
    "Also, tools such as planners and digital calendars can provide valuable "
    "structure. However, it is important to remember that effective time "
    "management is not about filling every moment with work - it involves "
    "striking a healthy balance between responsibilities and rest. In conclusion, "
    "mastering time management empowers individuals to achieve their goals while "
    "maintaining well-being.",

    # AI asked to sound like a casual human
    "ok so I finally tried that ramen place on 5th everyone keeps talking about. "
    "honestly? kind of overrated. the broth was good but like, $19 for a bowl is a "
    "lot, and they forgot my egg. my friend got the spicy one and said it was way "
    "better so maybe I just ordered wrong lol. would go back but probably not on "
    "purpose",

    # AI answering travel questions (Thai cooking classes, getting there)
    "Because they’re a really fun way to get into Thai food. Most start with a "
    "trip to a local market to learn the herbs and ingredients. Then you cook "
    "four or five dishes yourself, like pad thai, green curry and tom yum, and "
    "eat everything. They’re cheap, usually around $30 to $40, and Chiang Mai "
    "has some of the best ones, often on small organic farms outside town. The "
    "easiest way to get there is a minivan. It takes about two and a half to "
    "three hours, and most guesthouses in Khao Sok can book it and pick you up. "
    "If you’d like more comfort, a private taxi costs more but leaves when you "
    "want.",

    # AI short story (lighthouse keeper)
    """For thirty-one years, Mara Okonkwo kept the light on Gull Point. When the automated system arrived in October, the men from the coast authority shook her hand and gave her a plaque. They told her she could stay in the cottage until spring.

She didn’t know what to do with her evenings anymore. For three decades she had climbed the 114 steps at dusk to check the lamp, wipe salt from the glass and write the weather in the logbook. Now a small gray box did all of it. It blinked green and needed nothing from her.

On the ninth night of her retirement, someone knocked on her door.

It was a boy of about ten, soaked through, holding a flashlight that had run out. He said his family’s sailboat had come into the cove to wait out the wind, and he’d rowed the dinghy ashore to see the lighthouse up close. On the way back the fog had come in and he couldn’t find the boat.

Mara wrapped him in a blanket and put the kettle on. Then she looked out the window and her stomach dropped. The fog was so thick that the new beacon was only a faint smear of light. Its sensors read the conditions as normal, so it kept up its slow, polite rotation. Nothing was sounding.

“Your parents won’t be able to see the shore,” she said. “And you won’t be able to see them.”

She went to the shed and found the old brass foghorn, the hand-cranked one the authority had forgotten to take. It was stiff with rust. She oiled it the way her predecessor had taught her in 1995, carried it to the end of the jetty and began to crank.

The note was low and mournful, and it rolled out across the water.

A minute passed, then two. Her arms burned. The boy stood beside her with the blanket around his shoulders, counting her blasts.

Then, from somewhere in the gray, a voice called a name: “Teo! Teo!”

The boy shouted back, and a few minutes later a yellow light swung toward them out of the mist. His father was at the oars of a borrowed dinghy, his face pale with relief.

After they had gone, Mara stayed on the jetty a while. The automated beacon kept blinking behind her, faithful and unaware.

In the morning she wrote a letter to the coast authority. It was short. It said the foghorn should stay, and that someone should stay to crank it.

They wrote back in December. The answer was yes, and they asked whether she would be willing.

She framed the letter and hung it beside the plaque.""",
]

# Human writing that isn't mine: a travel forum post from about 15 years ago,
# before AI chatbots existed. Typos kept as written.
FORUM_POST = (
    'Took a ride to Wat Takien today. Great little find! For all those '
    '"authentiphiles", this place should definitely do the trick. The Temple, '
    'itself, is quite fun. There is quite a variety of opportunities to make '
    'merit, receive blessing, and partake of all the other nuances of Thai '
    'buddhism. There are dragons, tigers and dinosaurs figures for your '
    'enjoyment. Except for a couple amulet vendors, the "market" is all about '
    'eating. If you head over head over hungry. The market is open seven days, '
    'with weekends quite busy. There was a recent television pice that has '
    "really boosted it's popularity! But, during the week, the grounds are quite "
    'peaceful. I would say that the best means to get there would be to take the '
    'express boat to "Pibul 2" pier, pier #29. If you miss that, hop off at '
    'Nonthaburi, pier #30. From there, flag a taxi or two until you get one that '
    "knows Wat Takien. It's just before the Outer Ring Road."
)

HUMAN_TEXTS = [FORUM_POST] + MY_WRITING


SCENARIOS = [
    {
        # Criterion 1: at most 1 in 10 of my own pieces labelled AI.
        "name": "my own writing",
        "criterion": 1,
        "texts": MY_WRITING,
    },
    {
        # Criterion 2: the average AI score is at least 0.3 above the average
        # human score, using 5 AI and 5 human texts. Two scenarios, so the two
        # averages can be read off separately.
        "name": "AI texts",
        "criterion": 2,
        "texts": AI_TEXTS,
    },
    {
        "name": "human texts",
        "criterion": 2,
        "texts": HUMAN_TEXTS[:5],
    },
    {
        # Criterion 3: each label (human, unsure, ai) reached in every trial.
        # From my calibration runs: forum post -> human, my coffee-shop text ->
        # unsure, AI essay -> ai.
        "name": "label coverage",
        "criterion": 3,
        "texts": [AI_TEXTS[0], FORUM_POST, MY_WRITING[0]],
    },
    {
        # Criterion 5: empty, missing, null and over-20,000-character text each
        # get a 400, never a 500. Raw bodies, because "the field is missing"
        # can't be written as a text.
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},          # no text field at all
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": "word " * 5000, "creator_id": "eval_bad_huge"},  # 25,000 characters
        ],
    },

    # Criterion 4 (appeals) is not here. An appeal needs a submission first and
    # then its content_id, which a list of texts or bodies can't express.
    # I test it by hand with curl and record the results in the README.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
