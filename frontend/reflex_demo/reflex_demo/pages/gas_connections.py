"""The gas connections page."""

import reflex as rx
from ..backend.table_state import ElectrificationDashboardState
from ..templates import template


def gas_connections_trend_chart() -> rx.Component:
    """Create trend chart for gas connections."""
    return rx.recharts.line_chart(
        rx.recharts.line(
            data_key="total_connections",
            stroke=rx.color("orange", 9),
            type_="monotone",
        ),
        rx.recharts.x_axis(data_key="date"),
        rx.recharts.y_axis(),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.tooltip(),
        rx.recharts.legend(),
        data=ElectrificationDashboardState.gas_connections_chart_data,
        width="100%",
        height=400,
    )


def gas_connections_by_region_chart() -> rx.Component:
    """Create bar chart for gas connections by region."""
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="connections",
            fill=rx.color("orange", 7),
        ),
        rx.recharts.x_axis(data_key="region", angle=-45, text_anchor="end", height=100),
        rx.recharts.y_axis(),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.tooltip(),
        data=ElectrificationDashboardState.gas_connections_by_region_data,
        width="100%",
        height=450,
    )


def region_filter_selector() -> rx.Component:
    """Region filter component."""
    return rx.hstack(
        rx.text("Filter by Region:", size="3", weight="medium"),
        rx.text(
            "(Select from available regions)", size="2", color=rx.color("gray", 10)
        ),
        spacing="3",
        align="center",
    )


@template(
    route="/gas-connections",
    title="Gas Connections",
    on_load=ElectrificationDashboardState.load_data,
)
def gas_connections() -> rx.Component:
    """The gas connections page.

    Returns:
        The UI for the gas connections page.
    """
    return rx.vstack(
        rx.heading("Gas Connections Trends", size="7", weight="bold"),
        rx.text(
            "Monitor new gas connection installations across New Zealand",
            size="4",
            color=rx.color("gray", 11),
        ),
        rx.divider(),
        # Region filter
        rx.card(
            rx.vstack(
                region_filter_selector(),
                rx.text(
                    f"Total connections (last 12 months): {ElectrificationDashboardState.total_gas_connections_last_year:,}",
                    size="3",
                    weight="bold",
                ),
                spacing="3",
            ),
            size="3",
            width="100%",
        ),
        # Trend chart
        rx.card(
            rx.vstack(
                rx.heading("Gas Connections Over Time", size="5"),
                rx.text(
                    "Total new gas connections per month",
                    size="3",
                    color=rx.color("gray", 10),
                ),
                gas_connections_trend_chart(),
                spacing="4",
            ),
            size="3",
            width="100%",
        ),
        # Regional breakdown
        rx.card(
            rx.vstack(
                rx.heading("Gas Connections by Region (Latest Year)", size="5"),
                gas_connections_by_region_chart(),
                spacing="4",
            ),
            size="3",
            width="100%",
        ),
        # Info card
        rx.card(
            rx.vstack(
                rx.heading("About This Data", size="4"),
                rx.text(
                    "Gas connections data shows the number of new gas installations. "
                    "A declining trend indicates the shift away from gas towards electricity "
                    "and other renewable energy sources as part of New Zealand's electrification goals.",
                    size="3",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("info")),
                    rx.callout.text(
                        "Lower gas connections = Progress towards electrification"
                    ),
                    color_scheme="blue",
                ),
                spacing="3",
                align_items="start",
            ),
            size="3",
            width="100%",
        ),
        spacing="6",
        width="100%",
    )
