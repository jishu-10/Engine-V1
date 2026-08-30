from __future__ import annotations

AREA_VALUES = "values_priorities"
AREA_COMMUNICATION = "communication_social"
AREA_LIFESTYLE = "interests_lifestyle"
AREA_CONNECTION = "connection_style"

ALGORITHM_VERSION = "similarity_v1"
ONTOLOGY_VERSION = "1.0"
MAPPING_VERSION = "1.0"
PROMPT_VERSION = 1

AREAS = [
    {
        "id": AREA_VALUES,
        "name": "Values & Priorities",
        "weight": 0.30,
        "description": "What matters to the person when values conflict.",
    },
    {
        "id": AREA_COMMUNICATION,
        "name": "Communication & Social Style",
        "weight": 0.30,
        "description": "How the person naturally interacts with other people.",
    },
    {
        "id": AREA_LIFESTYLE,
        "name": "Interests & Lifestyle",
        "weight": 0.15,
        "description": "How the person prefers to spend time and experience life.",
    },
    {
        "id": AREA_CONNECTION,
        "name": "Connection Style",
        "weight": 0.25,
        "description": "What makes the person feel close and understood.",
    },
]

SIGNALS = [
    {
        "id": "V01",
        "area_id": AREA_VALUES,
        "name": "truth_honesty",
        "display_name": "Truth/Honesty Orientation",
        "description": "How strongly the person prioritizes truth over emotional comfort.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "V02",
        "area_id": AREA_VALUES,
        "name": "loyalty",
        "display_name": "Loyalty Orientation",
        "description": "How strongly the person prioritizes standing by people close to them.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "V03",
        "area_id": AREA_VALUES,
        "name": "fairness",
        "display_name": "Fairness Orientation",
        "description": "How strongly the person prioritizes fairness and equal treatment.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "V04",
        "area_id": AREA_VALUES,
        "name": "freedom",
        "display_name": "Freedom Orientation",
        "description": "Security/stability versus freedom/autonomy orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "V05",
        "area_id": AREA_VALUES,
        "name": "security",
        "display_name": "Security Orientation",
        "description": "Uncertainty tolerance versus security and predictability orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "AUX01",
        "area_id": AREA_VALUES,
        "name": "emotional_comfort",
        "display_name": "Emotional Comfort",
        "description": "Internal supporting axis from P01; not a primary V1 comparison signal.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": False,
    },
    {
        "id": "C01",
        "area_id": AREA_COMMUNICATION,
        "name": "directness",
        "display_name": "Directness",
        "description": "Indirect versus direct communication orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "C02",
        "area_id": AREA_COMMUNICATION,
        "name": "interpersonal_initiative",
        "display_name": "Interpersonal Initiative",
        "description": "How likely the person is to initiate interpersonal resolution or contact.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "C03",
        "area_id": AREA_COMMUNICATION,
        "name": "verbal_processing",
        "display_name": "Immediate Verbal Processing",
        "description": "Private processing versus immediate talk/process orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "C04",
        "area_id": AREA_COMMUNICATION,
        "name": "conflict_engagement",
        "display_name": "Conflict Engagement",
        "description": "Disengage/avoid versus engage/work through orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "C05",
        "area_id": AREA_COMMUNICATION,
        "name": "social_initiative",
        "display_name": "Social Initiative",
        "description": "Low initiation versus high social initiation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "C06",
        "area_id": AREA_COMMUNICATION,
        "name": "conversation_depth",
        "display_name": "Conversation Depth Orientation",
        "description": "Light/broad interaction versus deep/meaningful interaction.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "AUX02",
        "area_id": AREA_COMMUNICATION,
        "name": "uncertainty",
        "display_name": "Uncertainty",
        "description": "Auxiliary signal from P04; not a primary V1 comparison signal.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": False,
    },
    {
        "id": "L01",
        "area_id": AREA_LIFESTYLE,
        "name": "solitude_preference",
        "display_name": "Solitude Preference",
        "description": "Socially oriented versus solitude-oriented leisure preference.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "L02",
        "area_id": AREA_LIFESTYLE,
        "name": "spontaneity",
        "display_name": "Spontaneity",
        "description": "Planned versus spontaneous orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "L03",
        "area_id": AREA_LIFESTYLE,
        "name": "novelty_seeking",
        "display_name": "Novelty Seeking",
        "description": "Familiar versus novel preference.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "L04",
        "area_id": AREA_LIFESTYLE,
        "name": "planning_orientation",
        "display_name": "Planning Orientation",
        "description": "Improvisational versus planned orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "L05",
        "area_id": AREA_LIFESTYLE,
        "name": "exploration",
        "display_name": "Exploration",
        "description": "Familiarity versus exploration orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "L06",
        "area_id": AREA_LIFESTYLE,
        "name": "activity_social_leisure",
        "display_name": "Activity/Social Leisure Orientation",
        "description": "Preference for active social leisure versus quieter personal leisure.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "R01",
        "area_id": AREA_CONNECTION,
        "name": "closeness_preference",
        "display_name": "Closeness Preference",
        "description": "High independence versus high closeness preference.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "R02",
        "area_id": AREA_CONNECTION,
        "name": "independence_preference",
        "display_name": "Independence Preference",
        "description": "Shared-life orientation versus independent-life orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "R03",
        "area_id": AREA_CONNECTION,
        "name": "attentive_understanding",
        "display_name": "Attentive Understanding",
        "description": "Importance of someone remembering details and paying attention.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "R04",
        "area_id": AREA_CONNECTION,
        "name": "emotional_listening",
        "display_name": "Emotional Listening",
        "description": "Solution/action orientation versus listening/emotional processing orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "R05",
        "area_id": AREA_CONNECTION,
        "name": "honest_challenge",
        "display_name": "Honest Challenge",
        "description": "Acceptance/reassurance versus honest challenge orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
    {
        "id": "R06",
        "area_id": AREA_CONNECTION,
        "name": "authentic_acceptance",
        "display_name": "Authentic Acceptance",
        "description": "Interaction/feedback orientation versus acceptance/authenticity orientation.",
        "min_value": -1.0,
        "max_value": 1.0,
        "is_primary": True,
    },
]

PROMPTS = [
    {
        "prompt_id": "P01",
        "version": PROMPT_VERSION,
        "area_id": AREA_VALUES,
        "question_type": "trade_off",
        "question_text": "Someone you care about has done something that may hurt them if they hear the truth. What would you rather they receive from you?",
        "options": [
            {
                "key": "A",
                "text": "The honest truth, even if it's difficult to hear.",
                "mappings": {"V01": 1.0, "AUX01": -1.0},
            },
            {
                "key": "B",
                "text": "The truth, but softened carefully so it doesn't hurt unnecessarily.",
                "mappings": {"V01": 0.5, "AUX01": 0.3},
            },
            {
                "key": "C",
                "text": "Reassurance first; they can deal with the truth when they're ready.",
                "mappings": {"V01": -0.3, "AUX01": 0.7},
            },
            {
                "key": "D",
                "text": "If the truth isn't necessary, I'd rather spare them the pain.",
                "mappings": {"V01": -0.8, "AUX01": 1.0},
            },
        ],
    },
    {
        "prompt_id": "P02",
        "version": PROMPT_VERSION,
        "area_id": AREA_VALUES,
        "question_type": "trade_off",
        "question_text": "A close friend has clearly treated someone unfairly. What feels most right to you?",
        "options": [
            {
                "key": "A",
                "text": "Stand by my friend first and deal with the issue privately.",
                "mappings": {"V02": 1.0, "V03": -0.6},
            },
            {
                "key": "B",
                "text": "Support my friend, but make sure they acknowledge what they did.",
                "mappings": {"V02": 0.6, "V03": 0.4},
            },
            {
                "key": "C",
                "text": "Make sure the person who was treated unfairly is heard, even if my friend is upset with me.",
                "mappings": {"V02": -0.5, "V03": 1.0},
            },
            {
                "key": "D",
                "text": "Avoid taking sides and focus on preserving the friendship.",
                "mappings": {"V02": 0.4, "V03": 0.1},
            },
        ],
    },
    {
        "prompt_id": "P03",
        "version": PROMPT_VERSION,
        "area_id": AREA_VALUES,
        "question_type": "trade_off",
        "question_text": "You have two equally good opportunities. One gives you stability and predictability. The other gives you much more freedom but comes with uncertainty. Which would you naturally lean toward?",
        "options": [
            {
                "key": "A",
                "text": "The stable option — knowing what to expect matters to me.",
                "mappings": {"V04": -1.0, "V05": 1.0},
            },
            {
                "key": "B",
                "text": "Mostly stable, but I'd accept some uncertainty for more freedom.",
                "mappings": {"V04": -0.3, "V05": 0.5},
            },
            {
                "key": "C",
                "text": "Mostly freedom — I'd accept uncertainty for the possibilities it creates.",
                "mappings": {"V04": 0.5, "V05": -0.4},
            },
            {
                "key": "D",
                "text": "The freedom-first option — I'd rather figure things out as I go.",
                "mappings": {"V04": 1.0, "V05": -1.0},
            },
        ],
    },
    {
        "prompt_id": "P04",
        "version": PROMPT_VERSION,
        "area_id": AREA_COMMUNICATION,
        "question_type": "scenario",
        "question_text": "Someone you're close to suddenly seems distant. You don't know why. What's your most natural first reaction?",
        "options": [
            {
                "key": "A",
                "text": "Give them some space and let them come to me.",
                "mappings": {"C01": -0.8, "C02": -0.7, "AUX02": 0.4},
            },
            {
                "key": "B",
                "text": "Check in casually and see how they respond.",
                "mappings": {"C01": -0.2, "C02": 0.4, "AUX02": 0.0},
            },
            {
                "key": "C",
                "text": "Ask them directly if something is wrong.",
                "mappings": {"C01": 1.0, "C02": 0.9, "AUX02": -0.7},
            },
            {
                "key": "D",
                "text": "Wait for more information before doing anything.",
                "mappings": {"C01": -0.3, "C02": -0.5, "AUX02": 0.8},
            },
        ],
    },
    {
        "prompt_id": "P05",
        "version": PROMPT_VERSION,
        "area_id": AREA_COMMUNICATION,
        "question_type": "scenario",
        "question_text": "You're having a difficult conversation and emotions are starting to rise. What are you most likely to do?",
        "options": [
            {
                "key": "A",
                "text": "Keep talking — I'd rather work through it while it's happening.",
                "mappings": {"C03": 1.0, "C04": 0.9},
            },
            {
                "key": "B",
                "text": "Slow the conversation down but stay engaged.",
                "mappings": {"C03": 0.5, "C04": 0.8},
            },
            {
                "key": "C",
                "text": "Ask for some time to think, then come back to it.",
                "mappings": {"C03": -0.3, "C04": 0.4},
            },
            {
                "key": "D",
                "text": "Step away completely and revisit it only if necessary.",
                "mappings": {"C03": -0.8, "C04": -0.7},
            },
        ],
    },
    {
        "prompt_id": "P06",
        "version": PROMPT_VERSION,
        "area_id": AREA_COMMUNICATION,
        "question_type": "scenario",
        "question_text": "You arrive at a gathering where you only know one person. What are you most likely to find yourself doing?",
        "options": [
            {
                "key": "A",
                "text": "Stay mostly with the person I know or have a few one-to-one conversations.",
                "mappings": {"C05": -0.7, "C06": 0.4},
            },
            {
                "key": "B",
                "text": "Talk to a few new people if the opportunity comes naturally.",
                "mappings": {"C05": 0.1, "C06": 0.0},
            },
            {
                "key": "C",
                "text": "Move around and introduce myself to different people.",
                "mappings": {"C05": 1.0, "C06": -0.2},
            },
            {
                "key": "D",
                "text": "Find the most interesting conversation and get deeply involved in it, regardless of how many people are there.",
                "mappings": {"C05": 0.3, "C06": 1.0},
            },
        ],
    },
    {
        "prompt_id": "P07",
        "version": PROMPT_VERSION,
        "area_id": AREA_LIFESTYLE,
        "question_type": "preference",
        "question_text": "Your Saturday unexpectedly becomes completely free. Which option sounds most satisfying right now?",
        "options": [
            {
                "key": "A",
                "text": "Stay home, do my own thing and enjoy having no plans.",
                "mappings": {"L01": 1.0, "L02": -0.5, "L03": -0.4},
            },
            {
                "key": "B",
                "text": "Call someone and make spontaneous plans.",
                "mappings": {"L01": -0.4, "L02": 1.0, "L03": 0.3},
            },
            {
                "key": "C",
                "text": "Go somewhere I've never been or try something unfamiliar.",
                "mappings": {"L01": -0.2, "L02": 0.7, "L03": 1.0},
            },
            {
                "key": "D",
                "text": "Spend the day doing something I'm already really into.",
                "mappings": {"L01": 0.2, "L02": -0.4, "L03": -0.5},
            },
        ],
    },
    {
        "prompt_id": "P08",
        "version": PROMPT_VERSION,
        "area_id": AREA_LIFESTYLE,
        "question_type": "preference",
        "question_text": "You're planning a short trip with no particular destination in mind. Which sounds most appealing?",
        "options": [
            {
                "key": "A",
                "text": "Go somewhere I already know I'll enjoy.",
                "mappings": {"L03": -1.0, "L04": 0.8, "L05": -0.8},
            },
            {
                "key": "B",
                "text": "Mix something familiar with one new experience.",
                "mappings": {"L03": -0.2, "L04": 0.5, "L05": 0.1},
            },
            {
                "key": "C",
                "text": "Pick somewhere I've never been, but plan the important parts first.",
                "mappings": {"L03": 0.6, "L04": 0.4, "L05": 0.8},
            },
            {
                "key": "D",
                "text": "Choose a place almost at random and figure it out along the way.",
                "mappings": {"L03": 1.0, "L04": -0.8, "L05": 1.0},
            },
        ],
    },
    {
        "prompt_id": "P09",
        "version": PROMPT_VERSION,
        "area_id": AREA_CONNECTION,
        "question_type": "reflection",
        "question_text": "Which of these makes you feel most genuinely understood by someone?",
        "options": [
            {
                "key": "A",
                "text": "They remember the small things I've told them.",
                "mappings": {"R03": 1.0, "R04": 0.4, "R05": 0.1, "R06": 0.4},
            },
            {
                "key": "B",
                "text": "They listen without immediately trying to fix or change what I'm feeling.",
                "mappings": {"R03": 0.5, "R04": 1.0, "R05": 0.2, "R06": 0.6},
            },
            {
                "key": "C",
                "text": "They can challenge me honestly, even when I don't want to hear it.",
                "mappings": {"R03": 0.2, "R04": 0.2, "R05": 1.0, "R06": 0.4},
            },
            {
                "key": "D",
                "text": "I can be completely myself around them without having to explain every part of me.",
                "mappings": {"R03": 0.4, "R04": 0.5, "R05": 0.3, "R06": 1.0},
            },
        ],
    },
    {
        "prompt_id": "P10",
        "version": PROMPT_VERSION,
        "area_id": AREA_CONNECTION,
        "question_type": "preference",
        "question_text": "When you become close to someone, which feels most natural to you?",
        "options": [
            {
                "key": "A",
                "text": "I like being very involved in each other's lives and sharing a lot.",
                "mappings": {"R01": 1.0, "R02": -0.8},
            },
            {
                "key": "B",
                "text": "I like regular closeness, while still having plenty of our own space.",
                "mappings": {"R01": 0.4, "R02": 0.3},
            },
            {
                "key": "C",
                "text": "I feel closest when we're independent people who choose to spend meaningful time together.",
                "mappings": {"R01": -0.2, "R02": 0.8},
            },
            {
                "key": "D",
                "text": "I naturally need a lot of personal space, even with people I care about deeply.",
                "mappings": {"R01": -0.8, "R02": 1.0},
            },
        ],
    },
]


def primary_signal_ids() -> set[str]:
    return {signal["id"] for signal in SIGNALS if signal["is_primary"]}


def expected_mapping(prompt_id: str, option_key: str) -> dict[str, float]:
    for prompt in PROMPTS:
        if prompt["prompt_id"] == prompt_id:
            for option in prompt["options"]:
                if option["key"] == option_key:
                    return dict(option["mappings"])
    raise KeyError(f"Unknown mapping for {prompt_id}/{option_key}")

