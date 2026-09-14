from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ADVANCE_")

    app_name: str = "Advance-System"
    environment: str = "development"
    trading_mode: str = "PAPER"
    upstox_client_id: str | None = None
    upstox_client_secret: str | None = None
    upstox_redirect_uri: str | None = None
    upstox_access_token: str | None = None
    market_data_heartbeat_seconds: int = 15

    def live_execution_allowed(self) -> bool:
        return self.trading_mode.upper() == "LIVE" and self.environment.lower() == "production"


settings = Settings()
