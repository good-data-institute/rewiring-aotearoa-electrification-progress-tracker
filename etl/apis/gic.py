"""GIC Gas Industry Company API client for Registry Statistics."""

from pydantic import BaseModel, Field

from etl.core.http_api import HTTPAPIClient


class GICParams(BaseModel):
    """Parameters for GIC Registry Statistics.

    Note: GIC provides a single Excel file with all gas connection statistics.
    Date filtering happens during data processing.
    """

    url: str = Field(
        default="https://weblink.blob.core.windows.net/%24web/RegistryStats.xlsx",
        description="URL to GIC Registry Statistics Excel file",
    )

    sheet_name: str = Field(
        default="By Gas Gate", description="Excel sheet name to read for gas gate data"
    )

    region_sheet_name: str = Field(
        default="Gate Region",
        description="Excel sheet name for region concordance",
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class GICAPI(HTTPAPIClient):
    """API client for GIC Gas Industry Company Registry Statistics.

    This client fetches gas connection data from the Gas Industry Company
    Registry Statistics Excel file.

    The data includes new gas connections by gas gate and regional mapping.

    Example usage:
        >>> api = GICAPI()
        >>> api.fetch_data(output_path=Path("data/processed/gic/gic_raw.xlsx"))
    """

    base_url = "{url}"
    params_model = GICParams
    path_params = ["url"]

    def __init__(self, **params):
        """Initialize GIC API client.

        Args:
            **params: Parameters matching GICParams model.
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
        return "gic_gas_connections.xlsx"

    def _get_path_params(self):
        """Override to extract URL as path parameter."""
        if not self.params:
            return {}
        return {"url": self.params.url}
