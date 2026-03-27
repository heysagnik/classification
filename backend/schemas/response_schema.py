from pydantic import BaseModel, Field


class Feature(BaseModel):
    name: str
    coordinates: list[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="[x, y, width, height]",
    )


class AnalyzeResponse(BaseModel):
    classification: str
    features: list[Feature]
    description: str
    improvements: list[str]
    generated_image: str = Field(..., description="Base64 encoded generated image")


class HealthResponse(BaseModel):
    status: str = Field(..., description="API status")
    gemini_vision_configured: bool = Field(..., description="Whether Gemini vision key is configured")
    gemini_image_configured: bool = Field(..., description="Whether Gemini image key is configured")
    groq_configured: bool = Field(..., description="Whether Groq API is configured")
