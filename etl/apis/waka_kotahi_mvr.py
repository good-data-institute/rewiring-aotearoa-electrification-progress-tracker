"""Waka Kotahi Motor Vehicle Register API client."""

from pydantic import BaseModel, Field

from etl.core.http_api import HTTPAPIClient


class WakaKotahiMVRParams(BaseModel):
    """Parameters for Waka Kotahi Motor Vehicle Register.

    Note: The API returns the complete motor vehicle register dataset.
    The data is large (~5M+ rows) so streaming is recommended.
    """

    url: str = Field(
        default=(
            "https://hub.arcgis.com/api/v3/datasets/"
            "95182f7804bf4eeeac31b2747e841a70_0/downloads/data"
            "?format=csv&spatialRefId=2193&where=1%3D1"
        ),
        description="URL to Waka Kotahi Motor Vehicle Register CSV download",
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class WakaKotahiMVRAPI(HTTPAPIClient):
    """API client for Waka Kotahi Motor Vehicle Register.

    This client fetches motor vehicle registration data from the
    Waka Kotahi NZ Transport Agency Open Data Portal.

    The data includes all registered vehicles in New Zealand with details
    about registration date, location, vehicle type, fuel type, etc.

    Example usage:
        >>> api = WakaKotahiMVRAPI()
        >>> api.fetch_data(output_path=Path("data/raw/waka_kotahi_mvr/mvr_raw.csv"))
    """

    base_url = "{url}"
    params_model = WakaKotahiMVRParams
    path_params = ["url"]

    def __init__(self, **params):
        """Initialize Waka Kotahi MVR API client.

        Args:
            **params: Parameters matching WakaKotahiMVRParams model.
                     If not provided, defaults will be used.
        """
        if not params:
            params = {}
        super().__init__(**params)

    def get_default_output_filename(self) -> str:
        """Get default filename for saving API response.

        Returns:
            Filename string
        """
        return "waka_kotahi_mvr_raw.csv"

    def _get_path_params(self):
        """Override to extract URL as path parameter."""
        if not self.params:
            return {}
        return {"url": self.params.url}
