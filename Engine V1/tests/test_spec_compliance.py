from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import OptionSignalMapping, Prompt, PromptOption, Signal, SimilarityArea


EXPECTED_AREAS = {
    "values_priorities": ("Values & Priorities", 0.30),
    "communication_social": ("Communication & Social Style", 0.30),
    "interests_lifestyle": ("Interests & Lifestyle", 0.15),
    "connection_style": ("Connection Style", 0.25),
}


EXPECTED_SIGNALS = {
    "V01": ("values_priorities", -1.0, 1.0, True),
    "V02": ("values_priorities", -1.0, 1.0, True),
    "V03": ("values_priorities", -1.0, 1.0, True),
    "V04": ("values_priorities", -1.0, 1.0, True),
    "V05": ("values_priorities", -1.0, 1.0, True),
    "AUX01": ("values_priorities", -1.0, 1.0, False),
    "C01": ("communication_social", -1.0, 1.0, True),
    "C02": ("communication_social", -1.0, 1.0, True),
    "C03": ("communication_social", -1.0, 1.0, True),
    "C04": ("communication_social", -1.0, 1.0, True),
    "C05": ("communication_social", -1.0, 1.0, True),
    "C06": ("communication_social", -1.0, 1.0, True),
    "AUX02": ("communication_social", -1.0, 1.0, False),
    "L01": ("interests_lifestyle", -1.0, 1.0, True),
    "L02": ("interests_lifestyle", -1.0, 1.0, True),
    "L03": ("interests_lifestyle", -1.0, 1.0, True),
    "L04": ("interests_lifestyle", -1.0, 1.0, True),
    "L05": ("interests_lifestyle", -1.0, 1.0, True),
    "L06": ("interests_lifestyle", -1.0, 1.0, True),
    "R01": ("connection_style", -1.0, 1.0, True),
    "R02": ("connection_style", -1.0, 1.0, True),
    "R03": ("connection_style", -1.0, 1.0, True),
    "R04": ("connection_style", -1.0, 1.0, True),
    "R05": ("connection_style", -1.0, 1.0, True),
    "R06": ("connection_style", -1.0, 1.0, True),
}


EXPECTED_PROMPTS = {
    "P01": {
        "area_id": "values_priorities",
        "question_type": "trade_off",
        "question_text": "Someone you care about has done something that may hurt them if they hear the truth. What would you rather they receive from you?",
        "options": {
            "A": ("The honest truth, even if it's difficult to hear.", {"V01": 1.0, "AUX01": -1.0}),
            "B": ("The truth, but softened carefully so it doesn't hurt unnecessarily.", {"V01": 0.5, "AUX01": 0.3}),
            "C": ("Reassurance first; they can deal with the truth when they're ready.", {"V01": -0.3, "AUX01": 0.7}),
            "D": ("If the truth isn't necessary, I'd rather spare them the pain.", {"V01": -0.8, "AUX01": 1.0}),
        },
    },
    "P02": {
        "area_id": "values_priorities",
        "question_type": "trade_off",
        "question_text": "A close friend has clearly treated someone unfairly. What feels most right to you?",
        "options": {
            "A": ("Stand by my friend first and deal with the issue privately.", {"V02": 1.0, "V03": -0.6}),
            "B": ("Support my friend, but make sure they acknowledge what they did.", {"V02": 0.6, "V03": 0.4}),
            "C": ("Make sure the person who was treated unfairly is heard, even if my friend is upset with me.", {"V02": -0.5, "V03": 1.0}),
            "D": ("Avoid taking sides and focus on preserving the friendship.", {"V02": 0.4, "V03": 0.1}),
        },
    },
    "P03": {
        "area_id": "values_priorities",
        "question_type": "trade_off",
        "question_text": "You have two equally good opportunities. One gives you stability and predictability. The other gives you much more freedom but comes with uncertainty. Which would you naturally lean toward?",
        "options": {
            "A": ("The stable option \u2014 knowing what to expect matters to me.", {"V04": -1.0, "V05": 1.0}),
            "B": ("Mostly stable, but I'd accept some uncertainty for more freedom.", {"V04": -0.3, "V05": 0.5}),
            "C": ("Mostly freedom \u2014 I'd accept uncertainty for the possibilities it creates.", {"V04": 0.5, "V05": -0.4}),
            "D": ("The freedom-first option \u2014 I'd rather figure things out as I go.", {"V04": 1.0, "V05": -1.0}),
        },
    },
    "P04": {
        "area_id": "communication_social",
        "question_type": "scenario",
        "question_text": "Someone you're close to suddenly seems distant. You don't know why. What's your most natural first reaction?",
        "options": {
            "A": ("Give them some space and let them come to me.", {"C01": -0.8, "C02": -0.7, "AUX02": 0.4}),
            "B": ("Check in casually and see how they respond.", {"C01": -0.2, "C02": 0.4, "AUX02": 0.0}),
            "C": ("Ask them directly if something is wrong.", {"C01": 1.0, "C02": 0.9, "AUX02": -0.7}),
            "D": ("Wait for more information before doing anything.", {"C01": -0.3, "C02": -0.5, "AUX02": 0.8}),
        },
    },
    "P05": {
        "area_id": "communication_social",
        "question_type": "scenario",
        "question_text": "You're having a difficult conversation and emotions are starting to rise. What are you most likely to do?",
        "options": {
            "A": ("Keep talking \u2014 I'd rather work through it while it's happening.", {"C03": 1.0, "C04": 0.9}),
            "B": ("Slow the conversation down but stay engaged.", {"C03": 0.5, "C04": 0.8}),
            "C": ("Ask for some time to think, then come back to it.", {"C03": -0.3, "C04": 0.4}),
            "D": ("Step away completely and revisit it only if necessary.", {"C03": -0.8, "C04": -0.7}),
        },
    },
    "P06": {
        "area_id": "communication_social",
        "question_type": "scenario",
        "question_text": "You arrive at a gathering where you only know one person. What are you most likely to find yourself doing?",
        "options": {
            "A": ("Stay mostly with the person I know or have a few one-to-one conversations.", {"C05": -0.7, "C06": 0.4}),
            "B": ("Talk to a few new people if the opportunity comes naturally.", {"C05": 0.1, "C06": 0.0}),
            "C": ("Move around and introduce myself to different people.", {"C05": 1.0, "C06": -0.2}),
            "D": ("Find the most interesting conversation and get deeply involved in it, regardless of how many people are there.", {"C05": 0.3, "C06": 1.0}),
        },
    },
    "P07": {
        "area_id": "interests_lifestyle",
        "question_type": "preference",
        "question_text": "Your Saturday unexpectedly becomes completely free. Which option sounds most satisfying right now?",
        "options": {
            "A": ("Stay home, do my own thing and enjoy having no plans.", {"L01": 1.0, "L02": -0.5, "L03": -0.4}),
            "B": ("Call someone and make spontaneous plans.", {"L01": -0.4, "L02": 1.0, "L03": 0.3}),
            "C": ("Go somewhere I've never been or try something unfamiliar.", {"L01": -0.2, "L02": 0.7, "L03": 1.0}),
            "D": ("Spend the day doing something I'm already really into.", {"L01": 0.2, "L02": -0.4, "L03": -0.5}),
        },
    },
    "P08": {
        "area_id": "interests_lifestyle",
        "question_type": "preference",
        "question_text": "You're planning a short trip with no particular destination in mind. Which sounds most appealing?",
        "options": {
            "A": ("Go somewhere I already know I'll enjoy.", {"L03": -1.0, "L04": 0.8, "L05": -0.8}),
            "B": ("Mix something familiar with one new experience.", {"L03": -0.2, "L04": 0.5, "L05": 0.1}),
            "C": ("Pick somewhere I've never been, but plan the important parts first.", {"L03": 0.6, "L04": 0.4, "L05": 0.8}),
            "D": ("Choose a place almost at random and figure it out along the way.", {"L03": 1.0, "L04": -0.8, "L05": 1.0}),
        },
    },
    "P09": {
        "area_id": "connection_style",
        "question_type": "reflection",
        "question_text": "Which of these makes you feel most genuinely understood by someone?",
        "options": {
            "A": ("They remember the small things I've told them.", {"R03": 1.0, "R04": 0.4, "R05": 0.1, "R06": 0.4}),
            "B": ("They listen without immediately trying to fix or change what I'm feeling.", {"R03": 0.5, "R04": 1.0, "R05": 0.2, "R06": 0.6}),
            "C": ("They can challenge me honestly, even when I don't want to hear it.", {"R03": 0.2, "R04": 0.2, "R05": 1.0, "R06": 0.4}),
            "D": ("I can be completely myself around them without having to explain every part of me.", {"R03": 0.4, "R04": 0.5, "R05": 0.3, "R06": 1.0}),
        },
    },
    "P10": {
        "area_id": "connection_style",
        "question_type": "preference",
        "question_text": "When you become close to someone, which feels most natural to you?",
        "options": {
            "A": ("I like being very involved in each other's lives and sharing a lot.", {"R01": 1.0, "R02": -0.8}),
            "B": ("I like regular closeness, while still having plenty of our own space.", {"R01": 0.4, "R02": 0.3}),
            "C": ("I feel closest when we're independent people who choose to spend meaningful time together.", {"R01": -0.2, "R02": 0.8}),
            "D": ("I naturally need a lot of personal space, even with people I care about deeply.", {"R01": -0.8, "R02": 1.0}),
        },
    },
}


def test_area_weights_match_spec(db_session: Session) -> None:
    actual = {
        area.id: (area.name, area.weight)
        for area in db_session.scalars(select(SimilarityArea))
    }
    assert actual == EXPECTED_AREAS


def test_signal_ontology_matches_spec(db_session: Session) -> None:
    actual = {
        signal.id: (signal.area_id, signal.min_value, signal.max_value, signal.is_primary)
        for signal in db_session.scalars(select(Signal))
    }
    assert actual == EXPECTED_SIGNALS


def test_production_prompts_match_spec_exactly(db_session: Session) -> None:
    prompts = {
        prompt.prompt_id: prompt
        for prompt in db_session.scalars(select(Prompt).order_by(Prompt.prompt_id))
    }
    assert set(prompts) == set(EXPECTED_PROMPTS)

    for prompt_id, expected in EXPECTED_PROMPTS.items():
        prompt = prompts[prompt_id]
        assert prompt.version == 1
        assert prompt.area_id == expected["area_id"]
        assert prompt.question_type == expected["question_type"]
        assert prompt.question_text == expected["question_text"]

        options = {
            option.option_key: option
            for option in db_session.scalars(
                select(PromptOption).where(PromptOption.prompt_uid == prompt.uid)
            )
        }
        assert set(options) == set(expected["options"])

        for option_key, (option_text, mappings) in expected["options"].items():
            option = options[option_key]
            assert option.option_text == option_text
            actual_mappings = {
                mapping.signal_id: mapping.value
                for mapping in db_session.scalars(
                    select(OptionSignalMapping).where(
                        OptionSignalMapping.option_id == option.id
                    )
                )
            }
            assert actual_mappings == mappings


def test_mapping_rows_are_versioned(db_session: Session) -> None:
    versions = {
        row[0]
        for row in db_session.execute(select(OptionSignalMapping.mapping_version))
    }
    assert versions == {"1.0"}
