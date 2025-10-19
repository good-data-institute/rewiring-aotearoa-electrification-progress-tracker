"""Base API client with parameter validation."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from etl.core.config import get_settings


class BaseAPIClient(ABC):
    """Base class for API clients with Pydantic parameter validation.

    This is a minimal base class that only handles parameter validation
    and settings management. Subclasses implement their own data fetching
    logic based on their specific requirements (HTTP, Azure Blob, etc.).

    Subclasses should define:
    - params_model: A Pydantic model for parameter validation
    - get_default_output_filename(): Method to return default output filename
    """

    params_model: type[BaseModel] | None = None

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

    @abstractmethod
    def get_default_output_filename(self) -> str:
        """Get the default filename for saving API response.

        Returns:
            Default filename string
        """
        ...
