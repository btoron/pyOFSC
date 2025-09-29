"""Test configuration loader for OFSC v3.0 tests."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import tomllib
from pydantic import BaseModel
from dotenv import load_dotenv


class TestEnvironmentConfig(BaseModel):
    """Configuration for a test environment."""

    url: str
    client_id: str
    client_secret: str
    instance: str


class MockServerConfig(BaseModel):
    """Configuration for mock server."""

    url: str = "http://localhost:8080"
    client_id: str = "mock_client_id"
    client_secret: str = "mock_client_secret"
    record_mode: str = "replay"
    storage_path: str = "tests/mock_recordings"


class AsyncConfig(BaseModel):
    """Configuration for async test settings."""

    max_concurrent: int = 10
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1


class TestConfig(BaseModel):
    """Main test configuration."""

    coverage_target: int = 80
    report_format: str = "html"
    debug_on_failure: bool = True
    environments: Dict[str, TestEnvironmentConfig]
    mock_server: MockServerConfig
    async_config: AsyncConfig


def load_test_config() -> TestConfig:
    """Load test configuration with precedence:
    1. Environment variables (highest priority)
    2. .env file
    3. config.test.toml file
    4. Default values (lowest priority)
    """
    # Load .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Load base config from TOML file
    config_file = Path(__file__).parent / "config.test.toml"
    if config_file.exists():
        with open(config_file, "rb") as f:
            config_data = tomllib.load(f)
    else:
        config_data = {}

    # Override with environment variables
    config_data = _apply_env_overrides(config_data)

    # Create configuration objects
    test_config = config_data.get("test", {})

    environments = {}
    for env_name, env_data in test_config.get("environments", {}).items():
        environments[env_name] = TestEnvironmentConfig(**env_data)

    # Add environment from .env if available
    if all(
        os.getenv(var)
        for var in ["OFSC_INSTANCE", "OFSC_CLIENT_ID", "OFSC_CLIENT_SECRET"]
    ):
        environments["env"] = TestEnvironmentConfig(
            url=f"https://{os.getenv('OFSC_INSTANCE')}.fs.ocs.oraclecloud.com",
            client_id=os.getenv("OFSC_CLIENT_ID"),
            client_secret=os.getenv("OFSC_CLIENT_SECRET"),
            instance=os.getenv("OFSC_INSTANCE"),
        )

    mock_server = MockServerConfig(**test_config.get("mock_server", {}))
    async_config = AsyncConfig(**test_config.get("async", {}))

    return TestConfig(
        coverage_target=test_config.get("coverage_target", 80),
        report_format=test_config.get("report_format", "html"),
        debug_on_failure=test_config.get("debug_on_failure", True),
        environments=environments,
        mock_server=mock_server,
        async_config=async_config,
    )


def _apply_env_overrides(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to config data."""
    # Environment variables follow pattern: OFSC_TEST_{SECTION}_{KEY}
    # Example: OFSC_TEST_ENVIRONMENTS_DEV_INSTANCE

    for key, value in os.environ.items():
        if key.startswith("OFSC_TEST_"):
            # Parse the key structure
            parts = key[10:].lower().split("_")  # Remove OFSC_TEST_ prefix

            # Navigate and set the value in config_data
            current = config_data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

    return config_data


def get_test_environment(env_name: str = "env") -> Optional[TestEnvironmentConfig]:
    """Get specific test environment configuration."""
    config = load_test_config()
    return config.environments.get(env_name)
