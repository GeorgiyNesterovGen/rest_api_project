from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    CORS_ALLOWED_ORIGIN: list[str]

    @property
    def DATABASE_URL(self):
        # "postgresql+psycopg://postgres:postgres@127.0.0.1:15432/postgres"
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def GET_CORS(self):
        return self.CORS_ALLOWED_ORIGIN

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
