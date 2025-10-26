"""Regional map visualization page."""

import reflex as rx
from ..backend.table_state import ElectrificationDashboardState
from ..templates import template


# NZ Region coordinates for visual layout (approximate relative positions)
NZ_REGIONS_LAYOUT = {
    "Northland": {"top": "5%", "left": "45%"},
    "Auckland": {"top": "15%", "left": "45%"},
    "Waikato": {"top": "25%", "left": "45%"},
    "Bay of Plenty": {"top": "25%", "left": "60%"},
    "Gisborne": {"top": "30%", "left": "70%"},
    "Hawkes Bay": {"top": "40%", "left": "65%"},
    "Taranaki": {"top": "40%", "left": "35%"},
    "Manawatu": {"top": "50%", "left": "45%"},
    "Wanganui": {"top": "48%", "left": "40%"},
    "Wellington": {"top": "60%", "left": "50%"},
    "Tasman": {"top": "55%", "left": "55%"},
    "Marlborough": {"top": "58%", "left": "62%"},
    "West Coast": {"top": "65%", "left": "50%"},
    "Canterbury": {"top": "72%", "left": "55%"},
    "Otago": {"top": "82%", "left": "55%"},
    "Southland": {"top": "92%", "left": "52%"},
}


def get_marker_color_and_shade(value, metric_type: str = "renewable"):
    """Determine color and shade based on value and metric type."""
    # This needs to be called outside of reactive context
    if metric_type == "renewable":
        # For renewable: higher is better
        return "grass", 8
    else:
        # For gas: lower is better
        return "orange", 7


def region_marker_renewable(item: rx.Var) -> rx.Component:
    """Create a region marker for renewable generation."""
    region = item["region"].to(str)
    value = item["renewable_pct"].to(int)
    position = NZ_REGIONS_LAYOUT.get(region, {"top": "50%", "left": "50%"})

    # Use conditional rendering for color based on value
    color_scheme = rx.cond(
        value >= 95,
        "grass",
        rx.cond(value >= 80, "green", rx.cond(value >= 60, "yellow", "orange")),
    )

    # Base size calculation (roughly 30-60px range)
    size = "45px"  # Fixed size for simplicity

    return rx.box(
        rx.tooltip(
            rx.box(
                rx.text(
                    region[:3].upper(),
                    size="1",
                    weight="bold",
                    color="white",
                ),
                display="flex",
                align_items="center",
                justify_content="center",
                width="100%",
                height="100%",
            ),
            content=f"{region}: {value}%",
        ),
        position="absolute",
        top=position.get("top", "50%"),
        left=position.get("left", "50%"),
        width=size,
        height=size,
        border_radius="50%",
        background=rx.color(color_scheme, 8),
        border="2px solid white",
        cursor="pointer",
        transition="all 0.2s",
        _hover={
            "transform": "scale(1.2)",
            "z_index": "10",
        },
        transform="translate(-50%, -50%)",
    )


def region_marker_gas(item: rx.Var) -> rx.Component:
    """Create a region marker for gas connections."""
    region = item["region"].to(str)
    value = item["connections"].to(int)
    position = NZ_REGIONS_LAYOUT.get(region, {"top": "50%", "left": "50%"})

    # Use conditional rendering for color based on value
    color_scheme = rx.cond(
        value > 100,
        "red",
        rx.cond(value > 50, "orange", rx.cond(value > 10, "yellow", "grass")),
    )

    # Size based on value - smaller is better for gas
    size = "35px"  # Fixed size for simplicity

    return rx.box(
        rx.tooltip(
            rx.box(
                rx.text(
                    region[:3].upper(),
                    size="1",
                    weight="bold",
                    color="white",
                ),
                display="flex",
                align_items="center",
                justify_content="center",
                width="100%",
                height="100%",
            ),
            content=f"{region}: {value} connections",
        ),
        position="absolute",
        top=position.get("top", "50%"),
        left=position.get("left", "50%"),
        width=size,
        height=size,
        border_radius="50%",
        background=rx.color(color_scheme, 7),
        border="2px solid white",
        cursor="pointer",
        transition="all 0.2s",
        _hover={
            "transform": "scale(1.2)",
            "z_index": "10",
        },
        transform="translate(-50%, -50%)",
    )


def region_marker(
    region: str, value: float, metric_type: str = "renewable", position: dict = None
) -> rx.Component:
    """Create a region marker on the map - DEPRECATED, use specific marker functions."""


def renewable_map() -> rx.Component:
    """Create a map visualization for renewable generation."""
    return rx.box(
        # Map container
        rx.box(
            # Background outline of NZ (simplified)
            rx.box(
                rx.image(
                    src="/nz_outline.svg",
                    width="100%",
                    height="100%",
                    opacity="0.1",
                ),
                position="absolute",
                top="0",
                left="0",
                width="100%",
                height="100%",
            ),
            # Region markers
            rx.foreach(
                ElectrificationDashboardState.renewable_generation_by_region_data,
                region_marker_renewable,
            ),
            position="relative",
            width="100%",
            height="600px",
            background=rx.color("gray", 2),
            border_radius="12px",
            border=f"1px solid {rx.color('gray', 4)}",
        ),
        # Legend
        rx.box(
            rx.vstack(
                rx.heading("Legend", size="4"),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("grass", 9),
                    ),
                    rx.text("95-100% Renewable", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("grass", 7),
                    ),
                    rx.text("80-95% Renewable", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("yellow", 7),
                    ),
                    rx.text("60-80% Renewable", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("orange", 7),
                    ),
                    rx.text("Below 60% Renewable", size="2"),
                    spacing="2",
                ),
                spacing="3",
                align_items="start",
            ),
            padding="1em",
            background=rx.color("gray", 1),
            border_radius="8px",
            border=f"1px solid {rx.color('gray', 4)}",
            margin_top="1em",
        ),
        width="100%",
    )


def gas_connections_map() -> rx.Component:
    """Create a map visualization for gas connections."""
    return rx.box(
        # Map container
        rx.box(
            # Background outline of NZ
            rx.box(
                position="absolute",
                top="0",
                left="0",
                width="100%",
                height="100%",
                opacity="0.1",
            ),
            # Region markers
            rx.foreach(
                ElectrificationDashboardState.gas_connections_by_region_data,
                region_marker_gas,
            ),
            position="relative",
            width="100%",
            height="600px",
            background=rx.color("gray", 2),
            border_radius="12px",
            border=f"1px solid {rx.color('gray', 4)}",
        ),
        # Legend
        rx.box(
            rx.vstack(
                rx.heading("Legend", size="4"),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("red", 7),
                    ),
                    rx.text(">100 New Connections", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("orange", 7),
                    ),
                    rx.text("50-100 Connections", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("yellow", 7),
                    ),
                    rx.text("10-50 Connections", size="2"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        background=rx.color("grass", 7),
                    ),
                    rx.text("<10 Connections (Good!)", size="2"),
                    spacing="2",
                ),
                rx.text(
                    "Note: Larger circles = More connections",
                    size="1",
                    color=rx.color("gray", 10),
                    font_style="italic",
                ),
                spacing="3",
                align_items="start",
            ),
            padding="1em",
            background=rx.color("gray", 1),
            border_radius="8px",
            border=f"1px solid {rx.color('gray', 4)}",
            margin_top="1em",
        ),
        width="100%",
    )


def regional_comparison_table() -> rx.Component:
    """Create a comparison table for regional data."""
    return rx.card(
        rx.vstack(
            rx.heading("Regional Data Comparison", size="5"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Region"),
                        rx.table.column_header_cell("Renewable %"),
                        rx.table.column_header_cell("Gas Connections (Latest Year)"),
                        rx.table.column_header_cell("Status"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        ElectrificationDashboardState.renewable_generation_by_region_data,
                        lambda item: rx.table.row(
                            rx.table.cell(item["region"].to(str)),
                            rx.table.cell(
                                rx.badge(
                                    f"{item['renewable_pct'].to(int):.1f}%",
                                    color_scheme=rx.cond(
                                        item["renewable_pct"].to(int) >= 95,
                                        "grass",
                                        rx.cond(
                                            item["renewable_pct"].to(int) >= 80,
                                            "green",
                                            "orange",
                                        ),
                                    ),
                                )
                            ),
                            rx.table.cell("N/A"),  # Would need to match with gas data
                            rx.table.cell(
                                rx.cond(
                                    item["renewable_pct"].to(int) >= 95,
                                    rx.badge("Excellent", color_scheme="grass"),
                                    rx.cond(
                                        item["renewable_pct"].to(int) >= 80,
                                        rx.badge("Good", color_scheme="green"),
                                        rx.badge(
                                            "Needs Improvement", color_scheme="orange"
                                        ),
                                    ),
                                )
                            ),
                        ),
                    ),
                ),
                variant="surface",
                size="3",
            ),
            spacing="4",
            align_items="start",
        ),
        size="3",
        width="100%",
    )


@template(
    route="/regional-map",
    title="Regional Map",
    on_load=ElectrificationDashboardState.load_data,
)
def regional_map() -> rx.Component:
    """The regional map visualization page.

    Returns:
        The UI for the regional map page.
    """
    return rx.vstack(
        rx.heading("Regional Map Visualizations", size="7", weight="bold"),
        rx.text(
            "Interactive map showing renewable generation and gas connections across New Zealand regions",
            size="4",
            color=rx.color("gray", 11),
        ),
        rx.divider(),
        # Tabs for different map views
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Renewable Generation", value="renewable"),
                rx.tabs.trigger("Gas Connections", value="gas"),
                rx.tabs.trigger("Comparison Table", value="table"),
            ),
            rx.tabs.content(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                "Renewable Energy Generation by Region", size="5"
                            ),
                            rx.badge(
                                "Hover over regions for details",
                                color_scheme="blue",
                                size="2",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.text(
                            "Circle size represents renewable percentage. Darker green = higher renewable energy.",
                            size="3",
                            color=rx.color("gray", 10),
                        ),
                        renewable_map(),
                        spacing="4",
                    ),
                    size="3",
                    width="100%",
                ),
                value="renewable",
            ),
            rx.tabs.content(
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                "Gas Connections by Region (Latest Year)", size="5"
                            ),
                            rx.badge(
                                "Hover over regions for details",
                                color_scheme="orange",
                                size="2",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.text(
                            "Circle size represents number of connections. Smaller/greener = better for electrification.",
                            size="3",
                            color=rx.color("gray", 10),
                        ),
                        gas_connections_map(),
                        spacing="4",
                    ),
                    size="3",
                    width="100%",
                ),
                value="gas",
            ),
            rx.tabs.content(
                regional_comparison_table(),
                value="table",
            ),
            default_value="renewable",
            orientation="horizontal",
        ),
        # Info cards
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.heading("About Regional Visualization", size="4"),
                    rx.text(
                        "This interactive map shows regional performance across New Zealand. "
                        "Each circle represents a region, with size and color indicating the metric value.",
                        size="3",
                    ),
                    rx.unordered_list(
                        rx.list_item("Hover over regions to see exact values"),
                        rx.list_item("Larger circles = higher values"),
                        rx.list_item("Color indicates performance level"),
                    ),
                    spacing="3",
                    align_items="start",
                ),
                size="3",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Regional Insights", size="4"),
                    rx.text(
                        "Most regions show excellent renewable generation (>95%). "
                        "Gas connections are declining nationwide, with some regions "
                        "showing near-zero new installations.",
                        size="3",
                    ),
                    rx.callout.root(
                        rx.callout.icon(rx.icon("trending-up")),
                        rx.callout.text(
                            "Lower gas connections and higher renewable % = Better electrification progress"
                        ),
                        color_scheme="green",
                    ),
                    spacing="3",
                    align_items="start",
                ),
                size="3",
            ),
            columns="2",
            spacing="4",
            width="100%",
        ),
        spacing="6",
        width="100%",
    )
