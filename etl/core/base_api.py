"""Base API client for making HTTP requests with validation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests
from pydantic import BaseModel

from etl.core.config import get_settings


class BaseAPIClient(ABC):
    """Base class for API clients with Pydantic parameter validation.

    Subclasses should define:
    - base_url: The base URL for the API (can contain {placeholders} for path params)
    - params_model: A Pydantic model for parameter validation
    - path_params: List of parameter names that should be path params (not query params)
    """

    base_url: str = ""
    params_model: type[BaseModel] | None = None
    path_params: list[str] = []  # List of param names that are path params

    def __init__(self, **params):
        """Initialize API client with validated parameters.

        Args:
            **params: Parameters to be validated against params_model
        """
        self.settings = get_settings()

        # Validate and store parameters
        if self.params_model:
            self.params = self.params_model(**params)
        else:
            self.params = None

    def _get_path_params(self) -> dict[str, Any]:
        """Extract path parameters from the params model.

        Returns:
            Dictionary of path parameters
        """
        if not self.params:
            return {}

        params_dict = self.params.model_dump()

        # Only include params that are in the path_params list
        return {k: v for k, v in params_dict.items() if k in self.path_params}

    def _build_url(self, path_params: dict[str, Any] | None = None) -> str:
        """Build the complete URL with path parameters.

        Args:
            path_params: Optional dictionary of path parameters to substitute in URL.
                        If not provided, will extract from self.params.

        Returns:
            Complete URL string
        """
        if path_params is None:
            path_params = self._get_path_params()

        url = self.base_url
        if path_params:
            url = url.format(**path_params)
        return url

    def _get_query_params(self) -> dict[str, Any]:
        """Extract query parameters from the params model.

        Returns:
            Dictionary of query parameters (excluding path params)
        """
        if not self.params:
            return {}

        # Convert Pydantic model to dict
        params_dict = self.params.model_dump()

        # Filter out None values and path parameters
        return {
            k: v
            for k, v in params_dict.items()
            if v is not None and k not in self.path_params
        }

    def fetch_data(
        self, path_params: dict[str, Any] | None = None, output_path: Path | None = None
    ) -> bytes:
        """Fetch data from the API.

        Args:
            path_params: Dictionary of path parameters
            output_path: Optional path to save the response

        Returns:
            Response content as bytes

        Raises:
            requests.RequestException: If the request fails
        """
        url = self._build_url(path_params)
        query_params = self._get_query_params()

        print(f"Fetching data from: {url}")
        print(f"Query parameters: {query_params}")

        for attempt in range(self.settings.api_retry_attempts):
            try:
                response = requests.get(
                    url, params=query_params, timeout=self.settings.api_timeout
                )
                response.raise_for_status()

                # Save to file if output path provided
                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(response.content)
                    print(f"Data saved to: {output_path}")

                return response.content

            except requests.RequestException as e:
                if attempt == self.settings.api_retry_attempts - 1:
                    raise
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")

        raise RuntimeError("Max retries exceeded")

    @abstractmethod
    def get_default_output_filename(self) -> str:
        """Get the default filename for saving API response.

        Returns:
            Default filename string
        """
        pass
