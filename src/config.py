# python
from pydantic import BaseSettings, AnyHttpUrl, Field, validator


class Config(BaseSettings):
    CIRCLE_API_KEY: str = Field(..., env="CIRCLE_API_KEY")
    CIRCLE_BASE_URL: AnyHttpUrl = Field(
        default="https://api.circle.com/v1",
        env="CIRCLE_BASE_URL",
        description="Circle API base URL (v1)"
    )
    ARC_RPC_URL: AnyHttpUrl = Field(..., env="ARC_RPC_URL", description="ARC RPC endpoint")
    TREASURY_CONTRACT_ADDRESS: str = Field(..., env="TREASURY_CONTRACT_ADDRESS")
    DB_URL: str = Field(..., env="DB_URL")
    WEBHOOK_SECRET: str = Field(..., env="WEBHOOK_SECRET")

    @validator("TREASURY_CONTRACT_ADDRESS")
    def validate_contract_address(cls, v):
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Invalid Ethereum contract address format")
        return v.lower()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config()

