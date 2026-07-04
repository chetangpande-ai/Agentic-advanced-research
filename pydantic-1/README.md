# Pydantic Basics

This folder contains small, separate examples for common Pydantic concepts.

Each file is intentionally short and runnable on its own.

## Run Examples

From the project root:

```powershell
uv run python pydantic-1/00_plain_class_vs_pydantic.py
uv run python pydantic-1/01_base_model.py
uv run python pydantic-1/02_annotated_fields.py
uv run python pydantic-1/03_field_validator.py
uv run python pydantic-1/04_model_validator.py
uv run python pydantic-1/05_computed_field.py
uv run python pydantic-1/06_nested_models.py
```

## Learning Order

| File | Concept | What to Notice |
| --- | --- | --- |
| `00_plain_class_vs_pydantic.py` | Plain class vs Pydantic | Plain classes store values as-is; Pydantic validates and converts. |
| `01_base_model.py` | `BaseModel` | The core Pydantic class for validated data models. |
| `02_annotated_fields.py` | Annotated fields | Use `Annotated` and `Field` to attach constraints to normal Python types. |
| `03_field_validator.py` | Field validator | Validate or clean one field at a time. |
| `04_model_validator.py` | Model validator | Validate rules that depend on multiple fields. |
| `05_computed_field.py` | Computed field | Calculate output values from other model fields. |
| `06_nested_models.py` | Nested models | Validate objects inside objects, including lists of child models. |

## Mental Model

Pydantic is most useful at system boundaries:

- API request bodies
- API responses
- Config files
- LLM structured outputs
- Data loaded from JSON, CSV, databases, or tools

You define the shape of valid data once, and Pydantic handles validation, conversion, and useful error messages.

## Concept Summary

### BaseModel

`BaseModel` is the starting point.

```python
class User(BaseModel):
    name: str
    age: int
```

Pydantic validates input and converts compatible values, such as `"29"` to `29`.

### Annotated Fields

Use `Annotated` with `Field` when a field has constraints.

```python
Name = Annotated[str, Field(min_length=2, max_length=30)]
```

This keeps the type readable while adding validation rules.

### Field Validator

Use `@field_validator` when one field needs custom logic.

Good examples:

- trim whitespace
- lowercase an email
- reject invalid status values

### Model Validator

Use `@model_validator` when validation needs multiple fields.

Good examples:

- `end_date` must be after `start_date`
- `confirm_password` must match `password`
- `discount_price` must be less than `original_price`

### Computed Field

Use `@computed_field` when a value should be calculated, not passed in.

Good examples:

- order total
- full name
- age from date of birth

### Nested Models

Use nested models when your data has structure.

Example:

```text
Order
  Customer
    Address
  OrderItem[]
```

Pydantic validates the complete nested structure and tells you exactly where bad data lives.
