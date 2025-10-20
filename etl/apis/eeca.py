"""EECA Energy End Use Database API client."""

from pydantic import BaseModel, Field

from etl.core.http_api import HTTPAPIClient


class EECAParams(BaseModel):
    """Parameters for EECA Energy End Use Database.

    Note: EECA provides a single Excel file with all historical data.
    Date filtering happens during data processing.
    """

    url: str = Field(
        default="https://www.eeca.govt.nz/assets/EECA-Resources/Research-papers-guides/EEUD-Data-2017-2023.xlsx",
        description="URL to EECA Energy End Use Database Excel file",
    )

    sheet_name: str = Field(default="Data", description="Excel sheet name to read")

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class EECAAPI(HTTPAPIClient):
    """API client for EECA Energy End Use Database.

    This client fetches energy consumption data from the Energy Efficiency
    and Conservation Authority (EECA) Energy End Use Database.

    The data is provided as an Excel file containing energy consumption
    by sector and fuel type.

    Example usage:
        >>> api = EECAAPI()
        >>> api.fetch_data(output_path=Path("data/processed/eeca/eeca_raw.xlsx"))
    """

    base_url = "{url}"
    params_model = EECAParams
    path_params = ["url"]

    def __init__(self, **params):
        """Initialize EECA API client.

        Args:
            **params: Parameters matching EECAParams model.
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
        return "eeca_energy_consumption.xlsx"

    def _get_path_params(self):
        """Override to extract URL as path parameter."""
        if not self.params:
            return {}
        return {"url": self.params.url}
