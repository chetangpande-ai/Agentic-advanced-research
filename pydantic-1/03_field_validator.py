"""Field validator example.

Use field_validator when one field needs custom cleanup or validation.
"""

from pydantic import BaseModel, ValidationError, field_validator


class SignupForm(BaseModel):
    name: str
    email: str
    city: str

    @field_validator("name", "city")
    @classmethod
    def strip_and_title_case(cls, value: str) -> str:
        return value.strip().title()

    @field_validator("email")
    @classmethod
    def email_must_have_at_symbol(cls, value: str) -> str:
        cleaned_email = value.strip().lower()
        if "@" not in cleaned_email:
            raise ValueError("email must contain @")
        return cleaned_email


def main() -> None:
    form = SignupForm(
        name="  chetan  ",
        email="  CHETAN@example.COM ",
        city="  mumbai ",
    )

    print("Cleaned form:")
    print(form.model_dump())

    try:
        SignupForm(name="Chetan", email="invalid-email", city="Mumbai")
    except ValidationError as error:
        print("\nValidation error:")
        print(error.errors()[0]["msg"])


if __name__ == "__main__":
    main()
