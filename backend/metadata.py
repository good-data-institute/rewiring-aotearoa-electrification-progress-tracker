"""Metadata registry for all metrics in the system.

This module provides a centralized source of truth for metric metadata,
including descriptions, sources, dimensions, pipeline information, and dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MetricMetadata:
    """Metadata for a single metric."""

    dataset_key: str
    metric_id: str
    friendly_name: str
    description: str
    sector: str
    source_api: str
    pipeline_file: str
    pipeline_module: str  # Python module path for dynamic import
    input_file: str
    output_file: str
    dimensions: List[str]
    categories: Optional[List[str]] = None
    sub_categories: Optional[List[str]] = None
    fuel_types: Optional[List[str]] = None
    unit: str = "count"
    upstream_dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        return {
            "dataset_key": self.dataset_key,
            "metric_id": self.metric_id,
            "friendly_name": self.friendly_name,
            "description": self.description,
            "sector": self.sector,
            "source_api": self.source_api,
            "pipeline_file": self.pipeline_file,
            "pipeline_module": self.pipeline_module,
            "input_file": self.input_file,
            "output_file": self.output_file,
            "dimensions": self.dimensions,
            "categories": self.categories,
            "sub_categories": self.sub_categories,
            "fuel_types": self.fuel_types,
            "unit": self.unit,
            "upstream_dependencies": self.upstream_dependencies,
        }


# Complete metadata registry for all metrics
METRICS_METADATA: Dict[str, MetricMetadata] = {
    # ========== TRANSPORT METRICS (Waka Kotahi MVR) ==========
    "waka_kotahi_ev": MetricMetadata(
        dataset_key="waka_kotahi_ev",
        metric_id="_01_P1_EV",
        friendly_name="Waka Kotahi - EV Count",
        description="Number of Electric Vehicles (BEVs) in use by region, category, and sub-category",
        sector="Transport",
        source_api="Waka Kotahi MVR Open Data Portal",
        pipeline_file="etl/pipelines/_01_P1_EV.py",
        pipeline_module="etl.pipelines._01_P1_EV",
        input_file="data/processed/waka_kotahi_mvr/mvr_processed.parquet",
        output_file="data/metrics/waka_kotahi_mvr/01_P1_EV_analytics.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category", "Fuel_Type"],
        categories=["Private", "Commercial"],
        sub_categories=[
            "Light Passenger Vehicle",
            "Light Commercial Vehicle",
            "Bus",
        ],
        fuel_types=["BEV"],
        unit="count",
        upstream_dependencies=[
            "etl.pipelines.waka_kotahi_mvr.extract",
            "etl.pipelines.waka_kotahi_mvr.transform",
        ],
    ),
    "waka_kotahi_ff": MetricMetadata(
        dataset_key="waka_kotahi_ff",
        metric_id="_02_P1_FF",
        friendly_name="Waka Kotahi - Fossil Fuel Vehicles",
        description="Number of Fossil Fuel vehicles in use (Petrol, Diesel, HEV, PHEV, FCEV)",
        sector="Transport",
        source_api="Waka Kotahi MVR Open Data Portal",
        pipeline_file="etl/pipelines/_02_P1_FF.py",
        pipeline_module="etl.pipelines._02_P1_FF",
        input_file="data/processed/waka_kotahi_mvr/mvr_processed.parquet",
        output_file="data/metrics/waka_kotahi_mvr/02_P1_FF_analytics.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category", "Fuel_Type"],
        categories=["Private", "Commercial"],
        sub_categories=["Light Passenger Vehicle", "Light Commercial Vehicle"],
        fuel_types=["Petrol", "Diesel", "HEV", "PHEV", "FCEV"],
        unit="count",
        upstream_dependencies=[
            "etl.pipelines.waka_kotahi_mvr.extract",
            "etl.pipelines.waka_kotahi_mvr.transform",
        ],
    ),
    "waka_kotahi_new_ev": MetricMetadata(
        dataset_key="waka_kotahi_new_ev",
        metric_id="_03_P1_NewEV",
        friendly_name="Waka Kotahi - New EV Sales",
        description="Number of New (not used) EVs purchased",
        sector="Transport",
        source_api="Waka Kotahi MVR Open Data Portal",
        pipeline_file="etl/pipelines/_03_P1_NewEV.py",
        pipeline_module="etl.pipelines._03_P1_NewEV",
        input_file="data/processed/waka_kotahi_mvr/mvr_processed.parquet",
        output_file="data/metrics/waka_kotahi_mvr/03_P1_NewEV_analytics.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category", "Fuel_Type"],
        categories=["Private", "Commercial"],
        sub_categories=["Light Passenger Vehicle", "Light Commercial Vehicle"],
        fuel_types=["BEV"],
        unit="count",
        upstream_dependencies=[
            "etl.pipelines.waka_kotahi_mvr.extract",
            "etl.pipelines.waka_kotahi_mvr.transform",
        ],
    ),
    "waka_kotahi_used_ev": MetricMetadata(
        dataset_key="waka_kotahi_used_ev",
        metric_id="_04_P1_UsedEV",
        friendly_name="Waka Kotahi - Used EV Imports",
        description="Number of Used (imported) EVs purchased",
        sector="Transport",
        source_api="Waka Kotahi MVR Open Data Portal",
        pipeline_file="etl/pipelines/_04_P1_UsedEV.py",
        pipeline_module="etl.pipelines._04_P1_UsedEV",
        input_file="data/processed/waka_kotahi_mvr/mvr_processed.parquet",
        output_file="data/metrics/waka_kotahi_mvr/04_P1_UsedEV_analytics.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category", "Fuel_Type"],
        categories=["Private", "Commercial"],
        sub_categories=["Light Passenger Vehicle", "Light Commercial Vehicle"],
        fuel_types=["BEV"],
        unit="count",
        upstream_dependencies=[
            "etl.pipelines.waka_kotahi_mvr.extract",
            "etl.pipelines.waka_kotahi_mvr.transform",
        ],
    ),
    "waka_kotahi_fleet_elec": MetricMetadata(
        dataset_key="waka_kotahi_fleet_elec",
        metric_id="_05_P1_FleetElec",
        friendly_name="Waka Kotahi - Fleet Electrification",
        description="Percentage of vehicle fleet that is electrified (BEV)",
        sector="Transport",
        source_api="Waka Kotahi MVR Open Data Portal",
        pipeline_file="etl/pipelines/_05_P1_FleetElec.py",
        pipeline_module="etl.pipelines._05_P1_FleetElec",
        input_file="data/processed/waka_kotahi_mvr/mvr_processed.parquet",
        output_file="data/metrics/waka_kotahi_mvr/05_P1_FleetElec_analytics.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category"],
        categories=["Private", "Commercial"],
        sub_categories=["Light Passenger Vehicle", "Light Commercial Vehicle"],
        unit="percentage",
        upstream_dependencies=[
            "etl.pipelines.waka_kotahi_mvr.extract",
            "etl.pipelines.waka_kotahi_mvr.transform",
        ],
    ),
    # ========== SOLAR & BATTERY METRICS (EMI Battery/Solar) ==========
    "battery_penetration_commercial": MetricMetadata(
        dataset_key="battery_penetration_commercial",
        metric_id="_06a_P1_BattPen",
        friendly_name="EMI - Battery Penetration (Commercial)",
        description="Percentage of solar installs that include batteries (commercial sector)",
        sector="Solar & Batteries",
        source_api="EMI Battery & Solar API",
        pipeline_file="etl/pipelines/_06a_P1_BattPen.py",
        pipeline_module="etl.pipelines._06a_P1_BattPen",
        input_file="data/processed/emi_battery_solar/emi_battery_solar_cleaned.csv",
        output_file="data/metrics/emi_battery_solar/_06a_P1_BattPen.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category"],
        categories=["Solar", "Total"],
        sub_categories=["Commercial", "Residential", "Total"],
        unit="percentage",
        upstream_dependencies=[
            "etl.pipelines.emi_battery_solar.extract",
            "etl.pipelines.emi_battery_solar.transform",
        ],
    ),
    "battery_penetration_residential": MetricMetadata(
        dataset_key="battery_penetration_residential",
        metric_id="_06b_P1_BattPen",
        friendly_name="EMI - Battery Penetration (Residential)",
        description="Percentage of ICPs that include batteries (residential sector)",
        sector="Solar & Batteries",
        source_api="EMI Battery & Solar API",
        pipeline_file="etl/pipelines/_06b_P1_BattPen.py",
        pipeline_module="etl.pipelines._06b_P1_BattPen",
        input_file="data/processed/emi_battery_solar/emi_battery_solar_cleaned.csv",
        output_file="data/metrics/emi_battery_solar/_06b_P1_BattPen.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category"],
        categories=["Solar", "Total"],
        sub_categories=["Commercial", "Residential", "Total"],
        unit="percentage",
        upstream_dependencies=[
            "etl.pipelines.emi_battery_solar.extract",
            "etl.pipelines.emi_battery_solar.transform",
        ],
    ),
    "solar_penetration": MetricMetadata(
        dataset_key="solar_penetration",
        metric_id="_07_P1_Sol",
        friendly_name="EMI - Solar Capacity",
        description="Megawatts of solar capacity installed",
        sector="Solar & Batteries",
        source_api="EMI Battery & Solar API",
        pipeline_file="etl/pipelines/_07_P1_Sol.py",
        pipeline_module="etl.pipelines._07_P1_Sol",
        input_file="data/processed/emi_battery_solar/emi_battery_solar_cleaned.csv",
        output_file="data/metrics/emi_battery_solar/_07_P1_Sol.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category"],
        categories=["Solar", "Total"],
        sub_categories=["Commercial", "Residential", "Total"],
        unit="MW",
        upstream_dependencies=[
            "etl.pipelines.emi_battery_solar.extract",
            "etl.pipelines.emi_battery_solar.transform",
        ],
    ),
    "battery_capacity": MetricMetadata(
        dataset_key="battery_capacity",
        metric_id="_08_P1_Batt",
        friendly_name="EMI - Battery Capacity",
        description="Megawatts of battery capacity installed",
        sector="Solar & Batteries",
        source_api="EMI Battery & Solar API",
        pipeline_file="etl/pipelines/_08_P1_Batt.py",
        pipeline_module="etl.pipelines._08_P1_Batt",
        input_file="data/processed/emi_battery_solar/emi_battery_solar_cleaned.csv",
        output_file="data/metrics/emi_battery_solar/_08_P1_Batt.csv",
        dimensions=["Year", "Month", "Region", "Category", "Sub_Category"],
        categories=["Solar", "Total"],
        sub_categories=["Commercial", "Residential", "Total"],
        unit="MW",
        upstream_dependencies=[
            "etl.pipelines.emi_battery_solar.extract",
            "etl.pipelines.emi_battery_solar.transform",
        ],
    ),
    # ========== BUILDINGS & HEATING METRICS ==========
    "gic_analytics": MetricMetadata(
        dataset_key="gic_analytics",
        metric_id="_10_P1_Gas",
        friendly_name="GIC - Gas Connections",
        description="New gas connection installations by region",
        sector="Buildings & Heating",
        source_api="GIC API",
        pipeline_file="etl/pipelines/_10_P1_Gas.py",
        pipeline_module="etl.pipelines._10_P1_Gas",
        input_file="data/processed/gic/gic_gas_connections_cleaned.csv",
        output_file="data/metrics/gic/gic_gas_connections_analytics.csv",
        dimensions=["Year", "Month", "Region"],
        categories=["Total"],
        sub_categories=["Total"],
        unit="count",
        upstream_dependencies=[
            "etl.pipelines.gic.extract",
            "etl.pipelines.gic.transform",
        ],
    ),
    "eeca_boiler_energy": MetricMetadata(
        dataset_key="eeca_boiler_energy",
        metric_id="_11_P1_EnergyBoilers",
        friendly_name="EECA - Boiler Energy",
        description="Fossil fuel energy consumption in boilers (converted to MWh)",
        sector="Buildings & Heating",
        source_api="EECA API",
        pipeline_file="etl/pipelines/_11_P1_EnergyBoilers.py",
        pipeline_module="etl.pipelines._11_P1_EnergyBoilers",
        input_file="data/processed/eeca/eeca_energy_consumption_cleaned.csv",
        output_file="data/metrics/eeca/eeca_boilerenergy.csv",
        dimensions=["Year", "Category", "Sub_Category"],
        categories=["Total"],
        sub_categories=["Residential", "Commercial", "Industrial", "Total"],
        unit="MWh",
        upstream_dependencies=[
            "etl.pipelines.eeca.extract",
            "etl.pipelines.eeca.transform",
        ],
    ),
    # ========== ENERGY GRID METRICS ==========
    "emi_generation_analytics": MetricMetadata(
        dataset_key="emi_generation_analytics",
        metric_id="_12_P1_EnergyRenew",
        friendly_name="EMI - Renewable Generation",
        description="Renewable generation share (12-month rolling average percentage)",
        sector="Energy Grid",
        source_api="EMI Generation API",
        pipeline_file="etl/pipelines/_12_P1_EnergyRenew.py",
        pipeline_module="etl.pipelines._12_P1_EnergyRenew",
        input_file="data/processed/emi_generation/emi_generation_cleaned.csv",
        output_file="data/metrics/emi_generation/emi_generation_analytics.csv",
        dimensions=["Year", "Month", "Region"],
        categories=["Total"],
        sub_categories=["Total"],
        unit="percentage",
        upstream_dependencies=[
            "etl.pipelines.emi_generation.extract",
            "etl.pipelines.emi_generation.transform",
        ],
    ),
    "eeca_electricity_percentage": MetricMetadata(
        dataset_key="eeca_electricity_percentage",
        metric_id="_13_P1_ElecCons",
        friendly_name="EECA - Electricity Percentage",
        description="Electricity's share of total energy consumption",
        sector="Energy Grid",
        source_api="EECA API",
        pipeline_file="etl/pipelines/_13_P1_ElecCons.py",
        pipeline_module="etl.pipelines._13_P1_ElecCons",
        input_file="data/processed/eeca/eeca_energy_consumption_cleaned.csv",
        output_file="data/metrics/eeca/eeca_electricity_percentage.csv",
        dimensions=["Year"],
        categories=["Total"],
        sub_categories=["Total"],
        unit="percentage",
        upstream_dependencies=[
            "etl.pipelines.eeca.extract",
            "etl.pipelines.eeca.transform",
        ],
    ),
    "eeca_energy_by_fuel": MetricMetadata(
        dataset_key="eeca_energy_by_fuel",
        metric_id="_14_P1_EnergyxFuel",
        friendly_name="EECA - Energy by Fuel",
        description="Energy consumption breakdown by fuel type (converted to MWh)",
        sector="Energy Grid",
        source_api="EECA API",
        pipeline_file="etl/pipelines/_14_P1_EnergyxFuel.py",
        pipeline_module="etl.pipelines._14_P1_EnergyxFuel",
        input_file="data/processed/eeca/eeca_energy_consumption_cleaned.csv",
        output_file="data/metrics/eeca/eeca_energy_by_fuel.csv",
        dimensions=["Year", "Category", "Sub_Category"],
        categories=[
            "Coal",
            "Diesel",
            "Petrol",
            "Electricity",
            "LPG",
            "Natural Gas",
            "Total",
        ],
        sub_categories=[
            "Residential",
            "Commercial",
            "Industrial",
            "Agriculture",
            "Transport",
            "Total",
        ],
        unit="MWh",
        upstream_dependencies=[
            "etl.pipelines.eeca.extract",
            "etl.pipelines.eeca.transform",
        ],
    ),
}


def get_metadata(dataset_key: str) -> Optional[MetricMetadata]:
    """Get metadata for a specific dataset.

    Args:
        dataset_key: Dataset key to look up

    Returns:
        MetricMetadata object or None if not found
    """
    return METRICS_METADATA.get(dataset_key)


def get_all_metadata() -> Dict[str, MetricMetadata]:
    """Get metadata for all datasets.

    Returns:
        Dictionary of dataset_key -> MetricMetadata
    """
    return METRICS_METADATA


def get_metadata_by_sector() -> Dict[str, List[MetricMetadata]]:
    """Get metadata grouped by sector.

    Returns:
        Dictionary of sector -> List[MetricMetadata]
    """
    sectors = {}
    for metadata in METRICS_METADATA.values():
        if metadata.sector not in sectors:
            sectors[metadata.sector] = []
        sectors[metadata.sector].append(metadata)
    return sectors


def list_sectors() -> List[str]:
    """Get list of all unique sectors.

    Returns:
        List of sector names
    """
    return sorted(set(m.sector for m in METRICS_METADATA.values()))
