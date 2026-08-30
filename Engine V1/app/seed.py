from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.prompt_config import AREAS, MAPPING_VERSION, ONTOLOGY_VERSION, PROMPTS, SIGNALS
from app.db.session import SessionLocal
from app.models import (
    OptionSignalMapping,
    Prompt,
    PromptOption,
    Signal,
    SimilarityArea,
)


def seed_database(db: Session) -> None:
    for area_data in AREAS:
        area = db.get(SimilarityArea, area_data["id"])
        if area is None:
            area = SimilarityArea(id=area_data["id"])
            db.add(area)
        area.name = area_data["name"]
        area.weight = area_data["weight"]
        area.description = area_data["description"]

    for signal_data in SIGNALS:
        signal = db.get(Signal, signal_data["id"])
        if signal is None:
            signal = Signal(id=signal_data["id"])
            db.add(signal)
        signal.area_id = signal_data["area_id"]
        signal.name = signal_data["name"]
        signal.display_name = signal_data["display_name"]
        signal.description = signal_data["description"]
        signal.min_value = signal_data["min_value"]
        signal.max_value = signal_data["max_value"]
        signal.version = ONTOLOGY_VERSION
        signal.is_primary = signal_data["is_primary"]

    db.flush()

    for prompt_data in PROMPTS:
        prompt = db.scalar(
            select(Prompt).where(
                Prompt.prompt_id == prompt_data["prompt_id"],
                Prompt.version == prompt_data["version"],
            )
        )
        if prompt is None:
            prompt = Prompt(
                prompt_id=prompt_data["prompt_id"],
                version=prompt_data["version"],
            )
            db.add(prompt)
        prompt.area_id = prompt_data["area_id"]
        prompt.question_type = prompt_data["question_type"]
        prompt.question_text = prompt_data["question_text"]
        prompt.is_active = True
        db.flush()

        for order, option_data in enumerate(prompt_data["options"], start=1):
            option = db.scalar(
                select(PromptOption).where(
                    PromptOption.prompt_uid == prompt.uid,
                    PromptOption.option_key == option_data["key"],
                )
            )
            if option is None:
                option = PromptOption(
                    prompt_uid=prompt.uid,
                    option_key=option_data["key"],
                )
                db.add(option)
            option.option_text = option_data["text"]
            option.display_order = order
            db.flush()

            for signal_id, value in option_data["mappings"].items():
                mapping = db.scalar(
                    select(OptionSignalMapping).where(
                        OptionSignalMapping.option_id == option.id,
                        OptionSignalMapping.signal_id == signal_id,
                    )
                )
                if mapping is None:
                    mapping = OptionSignalMapping(
                        option_id=option.id,
                        signal_id=signal_id,
                    )
                    db.add(mapping)
                mapping.value = float(value)
                mapping.weight = 1.0
                mapping.mapping_version = MAPPING_VERSION

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_database(db)


if __name__ == "__main__":
    main()
