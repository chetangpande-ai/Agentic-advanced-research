"""Computed field example.

Use computed_field when a value should be calculated from other fields.
It appears in model exports, but you do not pass it as input.
"""

from pydantic import BaseModel, computed_field


class OrderLine(BaseModel):
    product_name: str
    quantity: int
    unit_price: float
    discount_percent: float = 0

    @computed_field
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

    @computed_field
    @property
    def total_after_discount(self) -> float:
        discount_amount = self.subtotal * (self.discount_percent / 100)
        return self.subtotal - discount_amount


def main() -> None:
    line = OrderLine(
        product_name="Notebook",
        quantity=5,
        unit_price=80,
        discount_percent=10,
    )

    print("Computed values:")
    print("Subtotal:", line.subtotal)
    print("Total after discount:", line.total_after_discount)

    print("\nExport includes computed fields:")
    print(line.model_dump())


if __name__ == "__main__":
    main()
