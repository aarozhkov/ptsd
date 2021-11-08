from typing import Optional


def filters_query(
    brand: Optional[str] = None,
    location: Optional[str] = None,
    partition: Optional[str] = None,
    status: Optional[str] = None,
):
    return {k: v for k, v in locals().items() if v is not None}
