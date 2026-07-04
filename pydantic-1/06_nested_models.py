"""Nested models example.

Use nested models when one object contains another object.
Pydantic validates the full structure, including child objects.
"""

from pydantic import BaseModel, Field, ValidationError


class Address(BaseModel):
    line_1: str
    city: str
    pincode: str = Field(pattern=r"^\d{6}$")


class Customer(BaseModel):
    name: str
    email: str
    address: Address


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)


class Order(BaseModel):
    order_id: str
    customer: Customer
    items: list[OrderItem]


def main() -> None:
    order = Order(
        order_id="ORD-1001",
        customer={
            "name": "Neha",
            "email": "neha@example.com",
            "address": {
                "line_1": "MG Road",
                "city": "Pune",
                "pincode": "411001",
            },
        },
        items=[
            {"sku": "BOOK-1", "quantity": 2},
            {"sku": "PEN-1", "quantity": 5},
        ],
    )

    print("Nested model object:")
    print(order)

    print("\nAccess nested values:")
    print(order.customer.address.city)
    print(order.items[0].sku)

    try:
        Order(
            order_id="ORD-1002",
            customer={
                "name": "Neha",
                "email": "neha@example.com",
                "address": {
                    "line_1": "MG Road",
                    "city": "Pune",
                    "pincode": "bad-pin",
                },
            },
            items=[{"sku": "BOOK-1", "quantity": 0}],
        )
    except ValidationError as error:
        print("\nValidation errors:")
        for issue in error.errors():
            location = ".".join(str(part) for part in issue["loc"])
            print(f"- {location}: {issue['msg']}")


if __name__ == "__main__":
    main()
