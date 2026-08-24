# backend/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str

    # LLM API
    llm_api_key: str
    llm_api_url: str = "https://api.openai.com/v1"

    # Auth / JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


"""Its one job: centralize all your app's settings/secrets in one place, loaded safely from
 environment variables.

Breaking that down:

1. It defines a Settings class — a blueprint listing every configuration value your backend needs to 
   run: the database connection string, your LLM API key, and the secret key used to sign login 
   tokens(JWT).
2. It reads those values from your .env file — instead of hardcoding secrets directly into your 
   Python code (which is a security risk, especially if you accidentally push it to GitHub), 
   the actual values live in .env, and config.py just knows how to load them.
3. It validates them — because it uses Pydantic, if .env is missing a required value 
   (like database_url), your app will fail immediately with a clear error when it starts up, 
   rather than crashing mysteriously later when some deep piece of code tries to use a value 
   that was never set.
4. It gives the rest of your app one shared, reusable "settings" object — every other file
   (database.py, llm_client.py, routers/dreams.py, etc.) will import get_settings() from this file
    instead of each independently trying to read environment variables. This means:
        -No duplicate logic scattered across files
        -One single source of truth for configuration
        -Easy to change a value later (edit .env, not code)
5. @lru_cache() makes it efficient — it ensures Python only readsand parses the .env file once, 
   the first time get_settings() is called, and reuses that same object every time after — 
   rather than re-reading the file on every request."""