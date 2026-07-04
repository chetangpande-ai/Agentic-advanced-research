"""Annotated fields example.

Annotated lets you keep the Python type and attach Pydantic constraints
using Field. This is very readable when fields have rules.
"""

from typing import Annotated

from pydantic import BaseModel, Field, ValidationError


Name = Annotated[str, Field(min_length=2, max_length=30)]
Pincode = Annotated[str, Field(pattern=r"^\d{6}$")]
PositiveQuantity = Annotated[int, Field(gt=0, le=100)]


class DeliveryRequest(BaseModel):
    customer_name: Name
    pincode: Pincode
    quantity: PositiveQuantity
    priority: Annotated[str, Field(default="normal", examples=["normal", "urgent"])]


def main() -> None:
    request = DeliveryRequest(
        customer_name="Riya",
        pincode="400001",
        quantity=3,
    )

    print("Valid request:")
    print(request.model_dump())

    try:
        DeliveryRequest(customer_name="R", pincode="123", quantity=0)
    except ValidationError as error:
        print("\nValidation errors:")
        for issue in error.errors():
            print(f"- {issue['loc'][0]}: {issue['msg']}")


if __name__ == "__main__":
    main()
