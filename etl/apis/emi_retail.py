"""EMI Retail API client for electricity market data."""

from typing import Literal

from pydantic import BaseModel, Field

from etl.core.base_api import BaseAPIClient


# TODO: Update this model with all valid parameters and options
class EMIRetailParams(BaseModel):
    """Parameters for EMI Retail API with explicit valid options.

    This model defines all available parameters and their valid values
    for the EMI Retail electricity market data API.
    """

    report_id: Literal["GUEHMT"] = Field(
        default="GUEHMT", description="Report ID for the data to retrieve"
    )

    Capacity: Literal["All_Drilldown", "Generation", "Transmission", "Distribution"] = (
        Field(default="All_Drilldown", description="Capacity type to filter")
    )

    DateFrom: str = Field(
        default="20130901",
        description="Start date in YYYYMMDD format",
        pattern=r"^\d{8}$",
    )

    DateTo: str = Field(
        default="20250831",
        description="End date in YYYYMMDD format",
        pattern=r"^\d{8}$",
    )

    RegionType: Literal[
        "NZ",
        "ZONE",
        "MAIN_CENTRE",
        "REG_COUNCIL",
        "NWK_REPORTING_REGION_DIST",
        "NWKP",
        "NSP_ROOT",
    ] = Field(
        default="NZ", description="Region type for data aggregation", alias="RegionType"
    )

    Capacity: Literal["All_Drilldown", "Generation", "Transmission", "Distribution"] = (
        Field(
            default="All_Drilldown",
            description="Capacity type to filter",
            alias="Capacity",
        )
    )

    FuelType: Literal[
        "All_Drilldown", "Coal", "Gas", "Hydro", "Wind", "Solar", "Other"
    ] = Field(
        default="All_Drilldown", description="Fuel type to filter", alias="FuelType"
    )

    # _rsdr: Literal["ALL", "PARTIAL"] = Field(
    #     default="ALL", description="Result set data range", alias="_rsdr"
    # )

    # _si: Literal["v|4", "v|3", "v|2"] = Field(
    #     default="v|4", description="Schema interface version", alias="_si"
    # )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True  # Allow using both field name and alias


class EMIRetailAPI(BaseAPIClient):
    """API client for EMI Retail electricity market data.

    This client fetches electricity market data from the New Zealand
    Electricity Authority (EA) EMI Retail data portal.

    Example usage:
        >>> api = EMIRetailAPI(DateFrom="20200101", DateTo="20240831")
        >>> api.fetch_data(output_path=Path("data/bronze/emi_retail.csv"))
    """

    base_url = "https://www.emi.ea.govt.nz/Retail/Download/DataReport/CSV/{report_id}"
    params_model = EMIRetailParams
    path_params = ["report_id"]  # report_id is a path parameter

    def __init__(self, **params):
        """Initialize EMI Retail API client.

        Args:
            **params: Parameters matching EMIRetailParams model.
                     If not provided, defaults will be used.
        """
        # Use defaults if no params provided
        if not params:
            params = {}
        super().__init__(**params)

    def get_default_output_filename(self) -> str:
        """Get default filename for saving API response.

        Returns:
            Filename string including date range
        """
        if self.params:
            date_from = self.params.DateFrom
            date_to = self.params.DateTo
            return f"emi_retail_{date_from}_{date_to}.csv"
        return "emi_retail.csv"
