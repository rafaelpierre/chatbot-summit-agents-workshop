from pydantic import BaseModel
from typing import Literal


class ConversationContext(BaseModel):
    product_tier: Literal["bronze", "silver", "gold", "unknown"] = "unknown"
