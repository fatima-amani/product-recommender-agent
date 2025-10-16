from pydantic import BaseModel, Field

class TTSTextModel(BaseModel):
    text: str = Field(..., description="The text to be converted to speech")