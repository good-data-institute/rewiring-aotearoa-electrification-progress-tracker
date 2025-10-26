"""The renewable generation page."""

import reflex as rx
from ..backend.table_state import ElectrificationDashboardState
from ..templates import template


def renewable_generation_by_region_chart() -> rx.Component:
    """Create bar chart for renewable generation by region."""
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="renewable_pct",
            fill=rx.color("grass", 7),
        ),
        rx.recharts.x_axis(data_key="region", angle=-45, text_anchor="end", height=120),
        rx.recharts.y_axis(domain=[0, 100]),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.tooltip(),
        data=ElectrificationDashboardState.renewable_generation_by_region_data,
        width="100%",
        height=500,
    )


@template(
    route="/renewable-generation",
    title="Renewable Generation",
    on_load=ElectrificationDashboardState.load_data,
)
def renewable_generation() -> rx.Component:
    """The renewable generation page.

    Returns:
        The UI for the renewable generation page.
    """
    return rx.vstack(
        rx.heading("Renewable Energy Generation", size="7", weight="bold"),
        rx.text(
            "Track renewable energy generation percentages across regions",
            size="4",
            color=rx.color("gray", 11),
        ),
        rx.divider(),
        # Summary card
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("leaf", size=32, color=rx.color("grass", 9)),
                    rx.vstack(
                        rx.heading(
                            f"{ElectrificationDashboardState.avg_renewable_percentage}%",
                            size="7",
                            color=rx.color("grass", 9),
                        ),
                        rx.text(
                            "Average Renewable Generation", size="4", weight="medium"
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    spacing="4",
                ),
                rx.text(
                    "This represents the average percentage of renewable energy across all regions",
                    size="3",
                    color=rx.color("gray", 10),
                ),
                spacing="3",
            ),
            size="3",
            width="100%",
        ),
        # Regional chart
        rx.card(
            rx.vstack(
                rx.heading("Renewable Generation by Region", size="5"),
                rx.text(
                    "Average renewable energy percentage for each region",
                    size="3",
                    color=rx.color("gray", 10),
                ),
                renewable_generation_by_region_chart(),
                spacing="4",
            ),
            size="3",
            width="100%",
        ),
        # Info cards
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.heading("High Performers", size="4"),
                    rx.text(
                        "Regions with near 100% renewable generation represent areas where "
                        "electricity comes almost entirely from renewable sources like hydro, "
                        "wind, and geothermal.",
                        size="3",
                    ),
                    spacing="3",
                    align_items="start",
                ),
                size="3",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Areas for Improvement", size="4"),
                    rx.text(
                        "Regions with lower percentages still rely on fossil fuel generation. "
                        "These areas are priorities for renewable energy infrastructure development.",
                        size="3",
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
        # About card
        rx.card(
            rx.vstack(
                rx.heading("About This Metric", size="4"),
                rx.text(
                    "The renewable generation percentage indicates what proportion of electricity "
                    "generation in each region comes from renewable sources (hydro, wind, solar, "
                    "geothermal) versus fossil fuels (coal, gas, oil).",
                    size="3",
                ),
                rx.callout.root(
                    rx.callout.icon(rx.icon("zap")),
                    rx.callout.text(
                        "New Zealand has a goal to reach 100% renewable electricity generation by 2030"
                    ),
                    color_scheme="green",
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
