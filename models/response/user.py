from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str