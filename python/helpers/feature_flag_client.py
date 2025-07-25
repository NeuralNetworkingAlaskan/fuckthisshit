import os
from typing import Optional

try:
    from flagsmith import Flagsmith
except ImportError:  # flagsmith may not be installed
    Flagsmith = None  # type: ignore


class FeatureFlagClient:
    """Simple wrapper for retrieving feature flags via Flagsmith."""

    _client: Optional["Flagsmith"] = None
    _initialized: bool = False

    @classmethod
    def _init_client(cls) -> None:
        if cls._initialized:
            return
        env_key = os.getenv("FLAGSMITH_ENVIRONMENT_KEY")
        if env_key and Flagsmith:
            api_url = os.getenv("FLAGSMITH_API_URL", "https://edge.flagsmith.com/api/v1/")
            try:
                cls._client = Flagsmith(environment_key=env_key, api_url=api_url)
            except Exception:
                cls._client = None
        cls._initialized = True

    @classmethod
    def is_feature_enabled(cls, name: str, default: Optional[bool] = None) -> Optional[bool]:
        """Return the state of a feature flag if available."""
        cls._init_client()
        if cls._client:
            try:
                flags = cls._client.get_environment_flags()
                return bool(flags.is_feature_enabled(name))
            except Exception:
                pass
        return default
