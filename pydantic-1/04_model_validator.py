"""Model validator example.

Use model_validator when validation depends on more than one field.
"""

from datetime import date
from typing import Self

from pydantic import BaseModel, ValidationError, model_validator


class ProjectPlan(BaseModel):
    project_name: str
    start_date: date
    end_date: date
    owner: str

    @model_validator(mode="after")
    def end_date_must_be_after_start_date(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


def main() -> None:
    plan = ProjectPlan(
        project_name="Agent Basics",
        start_date="2026-07-01",
        end_date="2026-07-10",
        owner="Chetan",
    )

    print("Valid project plan:")
    print(plan.model_dump())

    try:
        ProjectPlan(
            project_name="Bad Plan",
            start_date="2026-07-10",
            end_date="2026-07-01",
            owner="Chetan",
        )
    except ValidationError as error:
        print("\nValidation error:")
        print(error.errors()[0]["msg"])


if __name__ == "__main__":
    main()
