from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # The Groq API Key will be read automatically from your .env file
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()