"""BaseModel example.

BaseModel is the main class you inherit from in Pydantic.
It gives you validation, type conversion, and export methods.
"""

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    name: str
    age: int
    is_active: bool = True


def main() -> None:
    user = User(name="Asha", age="29")

    print("Model object:")
    print(user)

    print("\nAccess fields:")
    print(user.name)
    print(user.age)
    print(user.is_active)

    print("\nExport as dict:")
    print(user.model_dump())

    print("\nExport as JSON:")
    print(user.model_dump_json(indent=2))

    try:
        User(name="Asha", age="twenty-nine")
    except ValidationError as error:
        print("\nValidation error:")
        print(error.errors()[0]["msg"])


if __name__ == "__main__":
    main()
