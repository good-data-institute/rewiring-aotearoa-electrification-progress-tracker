"""EMI Generation API client for electricity generation data from Azure Blob Storage."""

import re
from io import BytesIO

from azure.storage.blob import ContainerClient
from pydantic import BaseModel, Field

from etl.core.config import get_settings


class EMIGenerationParams(BaseModel):
    """Parameters for EMI Generation data from Azure Blob Storage.

    This model defines parameters for fetching electricity generation
    data from the EMI Azure Blob container.
    """

    container_url: str = Field(
        default="https://emidatasets.blob.core.windows.net/publicdata",
        description="Azure Blob Storage container URL",
    )

    blob_prefix: str = Field(
        default="Datasets/Wholesale/Generation/Generation_MD/",
        description="Prefix path for generation CSV files in blob storage",
    )

    year_from: int = Field(
        default=2020,
        description="Start year for data extraction (inclusive)",
        ge=2000,
        le=2030,
    )

    year_to: int = Field(
        default=2025,
        description="End year for data extraction (inclusive)",
        ge=2000,
        le=2030,
    )

    concordance_url: str = Field(
        default="https://www.emi.ea.govt.nz/Wholesale/Download/DataReport/CSV/R_NSPL_DR?_si=v|3",
        description="URL for POC to Region concordance data",
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class EMIGenerationAPI:
    """API client for EMI Generation data from Azure Blob Storage.

    This client fetches electricity generation data from the EMI public
    Azure Blob Storage container. Unlike traditional REST APIs, this
    client uses the Azure SDK to access blob storage.

    Example usage:
        >>> api = EMIGenerationAPI(year_from=2020, year_to=2025)
        >>> csv_files = api.fetch_generation_data()
        >>> concordance = api.fetch_concordance()
    """

    def __init__(
        self,
        year_from: int = 2020,
        year_to: int = 2025,
        container_url: str = None,
        blob_prefix: str = None,
        concordance_url: str = None,
    ):
        """Initialize EMI Generation API client.

        Args:
            year_from: Start year for data extraction
            year_to: End year for data extraction
            container_url: Azure container URL (optional)
            blob_prefix: Blob prefix path (optional)
            concordance_url: Concordance data URL (optional)
        """
        params = {
            "year_from": year_from,
            "year_to": year_to,
        }
        if container_url:
            params["container_url"] = container_url
        if blob_prefix:
            params["blob_prefix"] = blob_prefix
        if concordance_url:
            params["concordance_url"] = concordance_url

        self.params = EMIGenerationParams(**params)
        self.settings = get_settings()

    def fetch_generation_data(self) -> list[tuple[str, BytesIO]]:
        """Fetch generation CSV files from Azure Blob Storage.

        Returns:
            List of tuples containing (blob_name, data_stream) for each CSV file

        Raises:
            ValueError: If no CSV files found in specified year range
        """
        container = ContainerClient.from_container_url(self.params.container_url)

        csv_files = []

        print("Connecting to EMI Azure Blob container...")
        print(
            f"Scanning for Generation_MD CSV files ({self.params.year_from}-{self.params.year_to})..."
        )

        for blob in container.list_blobs(name_starts_with=self.params.blob_prefix):
            if blob.name.endswith(".csv"):
                match = re.search(r"/(20\d{2})", blob.name)
                if match:
                    year = int(match.group(1))
                    if self.params.year_from <= year <= self.params.year_to:
                        print(f"  Found: {blob.name}")
                        stream = container.download_blob(blob.name)
                        data = BytesIO(stream.readall())
                        csv_files.append((blob.name, data))

        if not csv_files:
            raise ValueError(
                f"No generation CSV files found for years {self.params.year_from}-{self.params.year_to}"
            )

        print(f"✓ Found {len(csv_files)} CSV files")
        return csv_files

    def fetch_concordance(self) -> bytes:
        """Fetch POC to Region concordance data.

        Returns:
            CSV data as bytes

        Raises:
            requests.RequestException: If the request fails
        """
        import requests

        print(f"Fetching concordance data from: {self.params.concordance_url}")

        response = requests.get(
            self.params.concordance_url, timeout=self.settings.api_timeout
        )
        response.raise_for_status()

        print("✓ Concordance data fetched")
        return response.content

    def get_default_output_filename(self) -> str:
        """Get default filename for saving generation data.

        Returns:
            Filename string including year range
        """
        return f"emi_generation_{self.params.year_from}_{self.params.year_to}.csv"
