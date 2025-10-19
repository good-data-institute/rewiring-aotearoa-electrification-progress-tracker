"""HTTP API client for making REST API requests."""

from pathlib import Path
from typing import Any

import requests

from etl.core.base_api import BaseAPIClient


class HTTPAPIClient(BaseAPIClient):
    """HTTP API client for REST APIs with URL building and request handling.

    This class extends BaseAPIClient to add HTTP-specific functionality like:
    - URL building with path and query parameters
    - HTTP GET requests with retry logic
    - Response handling and file saving

    Subclasses should define:
    - base_url: The base URL for the API (can contain {placeholders} for path params)
    - params_model: A Pydantic model for parameter validation
    - path_params: List of parameter names that should be path params (not query params)
    - get_default_output_filename(): Method to return default output filename
    """

    base_url: str = ""
    path_params: list[str] = []  # List of param names that are path params

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
        """Fetch data from the API via HTTP GET request.

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
        if query_params:
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
