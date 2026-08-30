"""Environment variables validation.

Ensures all required environment variables are present and valid before
the application starts. This prevents runtime errors due to missing
or misconfigured environment variables.
"""
import os
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Raised when environment validation fails."""


def validate_required_vars(required_vars: Dict[str, str]) -> None:
    """Validate that all required environment variables are set.

    Args:
        required_vars: Dictionary of variable names to their descriptions

    Raises:
        ValidationError: If any required variable is missing or empty
    """
    missing: List[str] = []
    for var_name, description in required_vars.items():
        value = os.environ.get(var_name)
        if not value:
            missing.append(f"{var_name} ({description})")

    if missing:
        raise ValidationError(
            f"Missing required environment variables:\n" + "\n".join(f"  - {m}" for m in missing)
        )


def validate_port(value: str, var_name: str = "PORT") -> int:
    """Validate that a port number is valid.

    Args:
        value: Port number as string
        var_name: Name of the environment variable (for error messages)

    Returns:
        Validated port as integer

    Raises:
        ValidationError: If port is invalid
    """
    try:
        port = int(value)
        if not 1 <= port <= 65535:
            raise ValidationError(f"{var_name} must be between 1 and 65535, got {port}")
        return port
    except ValueError as e:
        raise ValidationError(f"{var_name} must be a valid integer, got {value}") from e


def validate_boolean(value: str, var_name: str = "BOOL_VAR") -> bool:
    """Validate that a boolean environment variable is valid.

    Args:
        value: Boolean value as string
        var_name: Name of the environment variable (for error messages)

    Returns:
        Validated boolean value

    Raises:
        ValidationError: If value is not a valid boolean
    """
    truthy = {"true", "1", "yes", "on"}
    falsy = {"false", "0", "no", "off"}

    normalized = value.lower().strip()
    if normalized in truthy:
        return True
    if normalized in falsy:
        return False

    raise ValidationError(
        f"{var_name} must be a boolean (true/false, 1/0, yes/no, on/off), got {value}"
    )


def validate_env() -> None:
    """Validate all critical environment variables.

    This should be called early in the application startup process.
    """
    required_vars = {
        "SECRET_KEY": "Django secret key",
        "DEBUG": "Debug mode flag",
    }

    # Only validate DB vars if not using SQLite
    if not os.environ.get("USE_SQLITE", "").lower() in ("true", "1"):
        required_vars.update(
            {
                "POSTGRES_DB": "PostgreSQL database name",
                "POSTGRES_USER": "PostgreSQL username",
                "POSTGRES_PASSWORD": "PostgreSQL password",
                "POSTGRES_HOST": "PostgreSQL host",
                "POSTGRES_PORT": "PostgreSQL port",
            }
        )

    validate_required_vars(required_vars)

    # Validate specific formats
    if "POSTGRES_PORT" in os.environ:
        validate_port(os.environ["POSTGRES_PORT"], "POSTGRES_PORT")

    if "DEBUG" in os.environ:
        validate_boolean(os.environ["DEBUG"], "DEBUG")