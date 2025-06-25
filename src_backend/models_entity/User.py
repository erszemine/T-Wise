# models_entity/User.py
from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime
from typing import Optional
from enums import UserPosition

class User(Document):
    username: str
    password_hash: str
    # full_name yerine bunları kullanın:
    first_name: str
    last_name: str
    email: Optional[str] = None
    position: UserPosition = Field(default= None)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            PydanticObjectId: str
        }
        keep_updated = True
    model_config = {
        "from_attributes": True
    }