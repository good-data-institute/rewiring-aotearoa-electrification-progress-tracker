import csv
from pathlib import Path
from typing import List

import reflex as rx


# Data models for electrification data
class ElectricityPercentageData(rx.Base):
    """EECA Electricity Percentage data model."""

    year: int
    month: int
    electricity_percentage: float
    metric_group: str
    category: str
    sub_category: str


class EnergyByFuelData(rx.Base):
    """EECA Energy by Fuel data model."""

    year: int
    month: int
    category: str  # Fuel type
    sub_category: str  # Sector
    metric_group: str
    energy_value: float


class GasConnectionsData(rx.Base):
    """GIC Gas Connections data model."""

    year: int
    month: int
    region: str
    connections: float
    metric_group: str
    category: str
    sub_category: str


class RenewableGenerationData(rx.Base):
    """EMI Renewable Generation data model."""

    year: int
    month: int
    region: str
    metric_group: str
    category: str
    sub_category: str
    renewable_percentage: float


class Item(rx.Base):
    """The item class."""

    name: str
    payment: float
    date: str
    status: str


class TableState(rx.State):
    """The state class."""

    items: List[Item] = []

    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 12  # Number of rows per page

    @rx.event
    def set_search_value(self, value: str):
        self.search_value = value

    @rx.event
    def set_sort_value(self, value: str):
        self.sort_value = value

    @rx.var(cache=True)
    def filtered_sorted_items(self) -> List[Item]:
        items = self.items

        # Filter items based on selected item
        if self.sort_value:
            if self.sort_value in ["payment"]:
                items = sorted(
                    items,
                    key=lambda item: float(getattr(item, self.sort_value)),
                    reverse=self.sort_reverse,
                )
            else:
                items = sorted(
                    items,
                    key=lambda item: str(getattr(item, self.sort_value)).lower(),
                    reverse=self.sort_reverse,
                )

        # Filter items based on search value
        if self.search_value:
            search_value = self.search_value.lower()
            items = [
                item
                for item in items
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "name",
                        "payment",
                        "date",
                        "status",
                    ]
                )
            ]

        return items

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 1
        )

    @rx.var(cache=True, initial_value=[])
    def get_current_page(self) -> list[Item]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items[start_index:end_index]

    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def first_page(self):
        self.offset = 0

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.limit

    def load_entries(self):
        with Path("items.csv").open(mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.items = [Item(**row) for row in reader]
            self.total_items = len(self.items)

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()


class ElectrificationDashboardState(rx.State):
    """Main state for the electrification dashboard."""

    # Data storage
    electricity_percentage_data: List[ElectricityPercentageData] = []
    energy_by_fuel_data: List[EnergyByFuelData] = []
    gas_connections_data: List[GasConnectionsData] = []
    renewable_generation_data: List[RenewableGenerationData] = []

    # Filters
    start_year: int = 2020
    end_year: int = 2025
    selected_regions: List[str] = []
    available_regions: List[str] = []

    # Chart preferences
    chart_type: str = "area"  # area, bar, line

    # Loading state
    is_loading: bool = False

    @rx.event
    def set_start_year(self, year: str):
        """Set the start year filter."""
        self.start_year = int(year)

    @rx.event
    def set_end_year(self, year: str):
        """Set the end year filter."""
        self.end_year = int(year)

    @rx.event
    def toggle_chart_type(self):
        """Toggle between area and bar chart."""
        self.chart_type = "bar" if self.chart_type == "area" else "area"

    @rx.event
    def set_chart_type(self, chart_type: str):
        """Set the chart type."""
        self.chart_type = chart_type

    @rx.event
    def toggle_region(self, region: str):
        """Toggle region selection."""
        if region in self.selected_regions:
            self.selected_regions.remove(region)
        else:
            self.selected_regions.append(region)

    def load_data(self):
        """Load all CSV files."""
        self.is_loading = True

        # Get the project root (go up from frontend/reflex_demo to project root)
        project_root = Path(__file__).parent.parent.parent.parent.parent

        # Load EECA Electricity Percentage
        eeca_elec_path = (
            project_root
            / "data"
            / "metrics"
            / "eeca"
            / "eeca_electricity_percentage.csv"
        )
        if eeca_elec_path.exists():
            with open(eeca_elec_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.electricity_percentage_data = [
                    ElectricityPercentageData(
                        year=int(row["Year"]),
                        month=int(row["Month"]),
                        electricity_percentage=float(row["_13_P1_ElecCons"]),
                        metric_group=row["Metric Group"],
                        category=row["Category"],
                        sub_category=row["Sub-Category"],
                    )
                    for row in reader
                ]

        # Load EECA Energy by Fuel
        eeca_fuel_path = (
            project_root / "data" / "metrics" / "eeca" / "eeca_energy_by_fuel.csv"
        )
        if eeca_fuel_path.exists():
            with open(eeca_fuel_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.energy_by_fuel_data = [
                    EnergyByFuelData(
                        year=int(row["Year"]),
                        month=int(row["Month"]),
                        category=row["Category"],  # Fuel type
                        sub_category=row["Sub-Category"],  # Sector
                        metric_group=row["Metric Group"],
                        energy_value=float(row["_14_P1_EnergyxFuel"]),
                    )
                    for row in reader
                ]

        # Load GIC Gas Connections
        gic_path = (
            project_root
            / "data"
            / "metrics"
            / "gic"
            / "gic_gas_connections_analytics.csv"
        )
        if gic_path.exists():
            with open(gic_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.gas_connections_data = [
                    GasConnectionsData(
                        year=int(row["Year"]),
                        month=int(row["Month"]),
                        region=row["Region"],
                        connections=float(row["_10_P1_Gas"]),
                        metric_group=row["Metric Group"],
                        category=row["Category"],
                        sub_category=row["Sub-Category"],
                    )
                    for row in reader
                ]

        # Load EMI Renewable Generation
        emi_path = (
            project_root
            / "data"
            / "metrics"
            / "emi_generation"
            / "emi_generation_analytics.csv"
        )
        if emi_path.exists():
            with open(emi_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                self.renewable_generation_data = [
                    RenewableGenerationData(
                        year=int(row["Year"]),
                        month=int(row["Month"]),
                        region=row["Region"],
                        metric_group=row["Metric Group"],
                        category=row["Category"],
                        sub_category=row["Sub-Category"],
                        renewable_percentage=float(row["_12_P1_EnergyRenew"])
                        if row["_12_P1_EnergyRenew"]
                        else 0.0,
                    )
                    for row in reader
                ]

        # Extract unique regions
        regions_set = set()
        for item in self.gas_connections_data:
            if item.region and item.region != "Unknown":
                regions_set.add(item.region)
        for item in self.renewable_generation_data:
            if item.region and item.region != "Unknown":
                regions_set.add(item.region)
        self.available_regions = sorted(list(regions_set))

        self.is_loading = False

    @rx.var(cache=True)
    def filtered_electricity_data(self) -> List[ElectricityPercentageData]:
        """Get filtered electricity percentage data."""
        return [
            item
            for item in self.electricity_percentage_data
            if self.start_year <= item.year <= self.end_year
        ]

    @rx.var(cache=True)
    def filtered_energy_fuel_data(self) -> List[EnergyByFuelData]:
        """Get filtered energy by fuel data."""
        return [
            item
            for item in self.energy_by_fuel_data
            if self.start_year <= item.year <= self.end_year
        ]

    @rx.var(cache=True)
    def filtered_gas_data(self) -> List[GasConnectionsData]:
        """Get filtered gas connections data."""
        filtered = [
            item
            for item in self.gas_connections_data
            if self.start_year <= item.year <= self.end_year
        ]
        if self.selected_regions:
            filtered = [
                item for item in filtered if item.region in self.selected_regions
            ]
        return filtered

    @rx.var(cache=True)
    def filtered_renewable_data(self) -> List[RenewableGenerationData]:
        """Get filtered renewable generation data."""
        filtered = [
            item
            for item in self.renewable_generation_data
            if self.start_year <= item.year <= self.end_year
        ]
        if self.selected_regions:
            filtered = [
                item for item in filtered if item.region in self.selected_regions
            ]
        return filtered

    @rx.var(cache=True)
    def latest_electricity_percentage(self) -> float:
        """Get the most recent electricity percentage."""
        if not self.electricity_percentage_data:
            return 0.0
        latest = max(self.electricity_percentage_data, key=lambda x: (x.year, x.month))
        return round(latest.electricity_percentage, 2)

    @rx.var(cache=True)
    def total_gas_connections_last_year(self) -> int:
        """Get total gas connections in the last 12 months."""
        if not self.gas_connections_data:
            return 0

        # Get the most recent year/month
        latest = max(self.gas_connections_data, key=lambda x: (x.year, x.month))
        latest_year, latest_month = latest.year, latest.month

        # Calculate 12 months ago
        twelve_months_ago = latest_month - 12
        start_year = latest_year + (twelve_months_ago // 12)
        start_month = (
            twelve_months_ago % 12 if twelve_months_ago > 0 else twelve_months_ago + 12
        )
        if twelve_months_ago <= 0:
            start_year -= 1

        total = sum(
            item.connections
            for item in self.gas_connections_data
            if (
                item.year > start_year
                or (item.year == start_year and item.month >= start_month)
            )
            and (
                item.year < latest_year
                or (item.year == latest_year and item.month <= latest_month)
            )
        )
        return int(total)

    @rx.var(cache=True)
    def avg_renewable_percentage(self) -> float:
        """Get average renewable generation percentage."""
        if not self.renewable_generation_data:
            return 0.0

        # Filter for recent year
        recent_data = [
            item
            for item in self.renewable_generation_data
            if item.year >= self.end_year - 1
        ]
        if not recent_data:
            return 0.0

        avg = sum(item.renewable_percentage for item in recent_data) / len(recent_data)
        return round(avg * 100, 2)

    @rx.var(cache=True)
    def total_energy_consumption(self) -> int:
        """Get total energy consumption (latest month)."""
        if not self.energy_by_fuel_data:
            return 0

        # Get the most recent year/month
        latest = max(self.energy_by_fuel_data, key=lambda x: (x.year, x.month))
        latest_year, latest_month = latest.year, latest.month

        total = sum(
            item.energy_value
            for item in self.energy_by_fuel_data
            if item.year == latest_year and item.month == latest_month
        )
        return int(total)

    @rx.var(cache=True)
    def electricity_chart_data(self) -> list[dict]:
        """Get electricity percentage data formatted for charts."""
        data = []
        for item in self.filtered_electricity_data:
            data.append(
                {
                    "date": f"{item.year}-{item.month:02d}",
                    "_13_P1_ElecCons": round(item.electricity_percentage, 2),
                    "year": item.year,
                    "month": item.month,
                }
            )
        return data

    @rx.var(cache=True)
    def energy_by_fuel_chart_data(self) -> list[dict]:
        """Get energy by fuel data formatted for stacked charts."""
        # Aggregate by year, month, and fuel type
        aggregated = {}
        for item in self.filtered_energy_fuel_data:
            key = f"{item.year}-{item.month:02d}"
            if key not in aggregated:
                aggregated[key] = {
                    "date": key,
                    "year": item.year,
                    "month": item.month,
                }

            fuel = item.category
            if fuel not in aggregated[key]:
                aggregated[key][fuel] = 0
            aggregated[key][fuel] += item.energy_value

        return sorted(aggregated.values(), key=lambda x: (x["year"], x["month"]))

    @rx.var(cache=True)
    def energy_by_sector_chart_data(self) -> list[dict]:
        """Get energy by sector data formatted for charts."""
        # Aggregate by year, month, and sector
        aggregated = {}
        for item in self.filtered_energy_fuel_data:
            key = f"{item.year}-{item.month:02d}"
            if key not in aggregated:
                aggregated[key] = {
                    "date": key,
                    "year": item.year,
                    "month": item.month,
                }

            sector = item.sub_category
            if sector not in aggregated[key]:
                aggregated[key][sector] = 0
            aggregated[key][sector] += item.energy_value

        return sorted(aggregated.values(), key=lambda x: (x["year"], x["month"]))

    @rx.var(cache=True)
    def gas_connections_chart_data(self) -> list[dict]:
        """Get gas connections data formatted for charts."""
        # Aggregate by year and month
        aggregated = {}
        for item in self.filtered_gas_data:
            key = f"{item.year}-{item.month:02d}"
            if key not in aggregated:
                aggregated[key] = {
                    "date": key,
                    "year": item.year,
                    "month": item.month,
                    "total_connections": 0,
                }
            aggregated[key]["total_connections"] += item.connections

        return sorted(aggregated.values(), key=lambda x: (x["year"], x["month"]))

    @rx.var(cache=True)
    def gas_connections_by_region_data(self) -> list[dict]:
        """Get gas connections by region for latest year."""
        if not self.filtered_gas_data:
            return []

        # Get latest year
        latest_year = max(item.year for item in self.filtered_gas_data)

        # Aggregate by region for latest year
        aggregated = {}
        for item in self.filtered_gas_data:
            if item.year == latest_year:
                if item.region not in aggregated:
                    aggregated[item.region] = 0
                aggregated[item.region] += item.connections

        return [
            {"region": region, "connections": connections}
            for region, connections in sorted(
                aggregated.items(), key=lambda x: x[1], reverse=True
            )
            if connections > 0
        ]

    @rx.var(cache=True)
    def renewable_generation_by_region_data(self) -> list[dict]:
        """Get average renewable generation by region."""
        if not self.filtered_renewable_data:
            return []

        # Aggregate by region
        aggregated = {}
        counts = {}
        for item in self.filtered_renewable_data:
            if item.region not in aggregated:
                aggregated[item.region] = 0
                counts[item.region] = 0
            aggregated[item.region] += item.renewable_percentage
            counts[item.region] += 1

        # Calculate averages
        return [
            {
                "region": region,
                "renewable_pct": round((aggregated[region] / counts[region]) * 100, 2),
            }
            for region in sorted(aggregated.keys())
            if counts[region] > 0 and region != "Unknown"
        ]
