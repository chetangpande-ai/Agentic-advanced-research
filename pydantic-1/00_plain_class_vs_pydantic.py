"""Why use Pydantic instead of a plain Python class?

Plain classes store data, but they do not validate input automatically.
Pydantic models store data and validate/coerce input at the boundary.
"""

from pydantic import BaseModel, ValidationError


class PlainFormData:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


class PydanticFormData(BaseModel):
    name: str
    age: int


def main() -> None:
    plain_form = PlainFormData(name="Chetan", age="35")
    print("Plain class age value:", plain_form.age)
    print("Plain class age type:", type(plain_form.age).__name__)

    pydantic_form = PydanticFormData(name="Chetan", age="35")
    print("\nPydantic age value:", pydantic_form.age)
    print("Pydantic age type:", type(pydantic_form.age).__name__)

    try:
        PydanticFormData(name="Chetan", age="not-a-number")
    except ValidationError as error:
        print("\nValidation error:")
        print(error.errors()[0]["msg"])


if __name__ == "__main__":
    main()
