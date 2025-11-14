from app.models.dtoModels.EntityDTO import Entity


class TokenDTO(Entity):
    access_token: str
    refresh_token: str
    token_type: str

