"""The electrification progress page."""

import reflex as rx
from ..backend.table_state import ElectrificationDashboardState
from ..templates import template


def electrification_chart() -> rx.Component:
    """Create the electrification progress chart."""
    return rx.recharts.area_chart(
        rx.recharts.area(
            data_key="_13_P1_ElecCons",
            stroke=rx.color("blue", 9),
            fill=rx.color("blue", 8),
            type_="monotone",
        ),
        rx.recharts.x_axis(data_key="date", label="Date"),
        rx.recharts.y_axis(label="Electricity %"),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.tooltip(),
        rx.recharts.legend(),
        data=ElectrificationDashboardState.electricity_chart_data,
        width="100%",
        height=400,
    )


@template(
    route="/electrification",
    title="Electrification Progress",
    on_load=ElectrificationDashboardState.load_data,
)
def electrification() -> rx.Component:
    """The electrification progress page.

    Returns:
        The UI for the electrification progress page.
    """
    return rx.vstack(
        rx.heading("Electrification Progress", size="7", weight="bold"),
        rx.text(
            "Track the percentage of energy from electricity over time",
            size="4",
            color=rx.color("gray", 11),
        ),
        rx.divider(),
        # Chart card
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Electricity Consumption Percentage", size="5"),
                    rx.badge(
                        f"Current: {ElectrificationDashboardState.latest_electricity_percentage}%",
                        color_scheme="blue",
                        size="2",
                    ),
                    justify="between",
                    width="100%",
                ),
                electrification_chart(),
                spacing="4",
            ),
            size="3",
            width="100%",
        ),
        # Info card
        rx.card(
            rx.vstack(
                rx.heading("About This Metric", size="4"),
                rx.text(
                    "This chart shows the percentage of total energy consumption that comes from electricity. "
                    "An increasing trend indicates progress in electrification as New Zealand transitions "
                    "away from fossil fuels.",
                    size="3",
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
