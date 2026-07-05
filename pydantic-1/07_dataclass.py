"""Dataclass example.

Python dataclasses are great for simple data containers.
Pydantic dataclasses look similar, but validate input values.
"""

from dataclasses import dataclass

from pydantic import ValidationError
from pydantic.dataclasses import dataclass as pydantic_dataclass


@dataclass
class PlainProduct:
    name: str
    quantity: int
    price: float


@pydantic_dataclass
class ValidatedProduct:
    name: str
    quantity: int
    price: float

    @property
    def total(self) -> float:
        return self.quantity * self.price


def main() -> None:
    plain_product = PlainProduct(name="Notebook", quantity="5", price="80")
    print("Plain dataclass:")
    print(plain_product)
    print("quantity type:", type(plain_product.quantity).__name__)
    print("price type:", type(plain_product.price).__name__)

    validated_product = ValidatedProduct(name="Notebook", quantity="5", price="80")
    print("\nPydantic dataclass:")
    print(validated_product)
    print("quantity type:", type(validated_product.quantity).__name__)
    print("price type:", type(validated_product.price).__name__)
    print("total:", validated_product.total)

    try:
        ValidatedProduct(name="Notebook", quantity="five", price="eighty")
    except ValidationError as error:
        print("\nValidation errors:")
        for issue in error.errors():
            print(f"- {issue['loc'][0]}: {issue['msg']}")


if __name__ == "__main__":
    main()
