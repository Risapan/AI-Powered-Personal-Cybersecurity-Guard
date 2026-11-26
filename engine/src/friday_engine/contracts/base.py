from pydantic import BaseModel, ConfigDict


class Contract(BaseModel):
    """Base for every data contract.

    - extra="forbid": unknown fields are an error, not silently dropped (T3, T8)
    - strict=True: no type coercion, so "1" is not quietly turned into 1
    - frozen=True: a finding can't be edited after it's built. Changes create a new object
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
        validate_default=True,
    )
