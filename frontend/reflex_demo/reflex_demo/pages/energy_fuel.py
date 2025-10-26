"""The energy by fuel page."""

import reflex as rx
from ..backend.table_state import ElectrificationDashboardState
from ..templates import template


def energy_fuel_stacked_chart() -> rx.Component:
    """Create stacked area chart for energy by fuel."""
    return rx.cond(
        ElectrificationDashboardState.chart_type == "area",
        rx.recharts.area_chart(
            rx.recharts.area(
                data_key="Electricity",
                stackId="1",
                stroke=rx.color("blue", 9),
                fill=rx.color("blue", 7),
            ),
            rx.recharts.area(
                data_key="Coal",
                stackId="1",
                stroke=rx.color("gray", 9),
                fill=rx.color("gray", 7),
            ),
            rx.recharts.area(
                data_key="Diesel",
                stackId="1",
                stroke=rx.color("orange", 9),
                fill=rx.color("orange", 7),
            ),
            rx.recharts.area(
                data_key="Petrol",
                stackId="1",
                stroke=rx.color("red", 9),
                fill=rx.color("red", 7),
            ),
            rx.recharts.area(
                data_key="Wood",
                stackId="1",
                stroke=rx.color("brown", 9),
                fill=rx.color("brown", 7),
            ),
            rx.recharts.area(
                data_key="Other",
                stackId="1",
                stroke=rx.color("purple", 9),
                fill=rx.color("purple", 7),
            ),
            rx.recharts.x_axis(data_key="date"),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.tooltip(),
            rx.recharts.legend(),
            data=ElectrificationDashboardState.energy_by_fuel_chart_data,
            width="100%",
            height=450,
        ),
        rx.recharts.bar_chart(
            rx.recharts.bar(
                data_key="Electricity",
                stack_id="1",
                fill=rx.color("blue", 7),
            ),
            rx.recharts.bar(
                data_key="Coal",
                stack_id="1",
                fill=rx.color("gray", 7),
            ),
            rx.recharts.bar(
                data_key="Diesel",
                stack_id="1",
                fill=rx.color("orange", 7),
            ),
            rx.recharts.bar(
                data_key="Petrol",
                stack_id="1",
                fill=rx.color("red", 7),
            ),
            rx.recharts.bar(
                data_key="Wood",
                stack_id="1",
                fill=rx.color("brown", 7),
            ),
            rx.recharts.bar(
                data_key="Other",
                stack_id="1",
                fill=rx.color("purple", 7),
            ),
            rx.recharts.x_axis(data_key="date"),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.tooltip(),
            rx.recharts.legend(),
            data=ElectrificationDashboardState.energy_by_fuel_chart_data,
            width="100%",
            height=450,
        ),
    )


def energy_sector_chart() -> rx.Component:
    """Create chart for energy by sector."""
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="Agriculture, Forestry and Fishing",
            fill=rx.color("green", 7),
        ),
        rx.recharts.bar(
            data_key="Commercial",
            fill=rx.color("blue", 7),
        ),
        rx.recharts.bar(
            data_key="Industrial",
            fill=rx.color("orange", 7),
        ),
        rx.recharts.bar(
            data_key="Residential",
            fill=rx.color("purple", 7),
        ),
        rx.recharts.bar(
            data_key="Transport",
            fill=rx.color("red", 7),
        ),
        rx.recharts.x_axis(data_key="date"),
        rx.recharts.y_axis(),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.tooltip(),
        rx.recharts.legend(),
        data=ElectrificationDashboardState.energy_by_sector_chart_data,
        width="100%",
        height=400,
    )


@template(
    route="/energy-fuel",
    title="Energy by Fuel",
    on_load=ElectrificationDashboardState.load_data,
)
def energy_fuel() -> rx.Component:
    """The energy by fuel page.

    Returns:
        The UI for the energy by fuel page.
    """
    return rx.vstack(
        rx.heading("Energy Consumption by Fuel Type", size="7", weight="bold"),
        rx.text(
            "Analyze energy consumption breakdown across different fuel sources",
            size="4",
            color=rx.color("gray", 11),
        ),
        rx.divider(),
        # Fuel type chart
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Energy by Fuel Type (Stacked)", size="5"),
                    rx.hstack(
                        rx.text("Chart Type:", size="3", weight="medium"),
                        rx.icon_button(
                            rx.icon("area-chart"),
                            size="2",
                            cursor="pointer",
                            variant="surface",
                            color_scheme=rx.cond(
                                ElectrificationDashboardState.chart_type == "area",
                                "blue",
                                "gray",
                            ),
                            on_click=lambda: ElectrificationDashboardState.set_chart_type(
                                "area"
                            ),
                        ),
                        rx.icon_button(
                            rx.icon("bar-chart-3"),
                            size="2",
                            cursor="pointer",
                            variant="surface",
                            color_scheme=rx.cond(
                                ElectrificationDashboardState.chart_type == "bar",
                                "blue",
                                "gray",
                            ),
                            on_click=lambda: ElectrificationDashboardState.set_chart_type(
                                "bar"
                            ),
                        ),
                        spacing="2",
                    ),
                    justify="between",
                    width="100%",
                ),
                energy_fuel_stacked_chart(),
                spacing="4",
            ),
            size="3",
            width="100%",
        ),
        # Sector chart
        rx.card(
            rx.vstack(
                rx.heading("Energy Consumption by Sector", size="5"),
                energy_sector_chart(),
                spacing="4",
            ),
            size="3",
            width="100%",
        ),
        # Legend info
        rx.card(
            rx.vstack(
                rx.heading("Fuel Types", size="4"),
                rx.grid(
                    rx.hstack(
                        rx.box(
                            width="20px",
                            height="20px",
                            background=rx.color("blue", 7),
                            border_radius="4px",
                        ),
                        rx.text("Electricity (Clean Energy)", size="3"),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.box(
                            width="20px",
                            height="20px",
                            background=rx.color("gray", 7),
                            border_radius="4px",
                        ),
                        rx.text("Coal (Fossil Fuel)", size="3"),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.box(
                            width="20px",
                            height="20px",
                            background=rx.color("orange", 7),
                            border_radius="4px",
                        ),
                        rx.text("Diesel (Fossil Fuel)", size="3"),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.box(
                            width="20px",
                            height="20px",
                            background=rx.color("red", 7),
                            border_radius="4px",
                        ),
                        rx.text("Petrol (Fossil Fuel)", size="3"),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.box(
                            width="20px",
                            height="20px",
                            background=rx.color("brown", 7),
                            border_radius="4px",
                        ),
                        rx.text("Wood (Biomass)", size="3"),
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.box(
                            width="20px",
                            height="20px",
                            background=rx.color("purple", 7),
                            border_radius="4px",
                        ),
                        rx.text("Other", size="3"),
                        spacing="2",
                    ),
                    columns="3",
                    spacing="4",
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
