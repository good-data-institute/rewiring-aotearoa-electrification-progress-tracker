"""The overview page of the app."""

import reflex as rx

from .. import styles
from ..backend.table_state import ElectrificationDashboardState
from ..templates import template


def kpi_card(
    title: str,
    value: str,
    icon: str,
    icon_color: str,
    trend_text: str = "",
    trend_value: str = "",
    trend_positive: bool = True,
) -> rx.Component:
    """Create a KPI card for the dashboard."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag=icon, size=34),
                    color_scheme=icon_color,
                    radius="full",
                    padding="0.7rem",
                ),
                rx.vstack(
                    rx.heading(
                        value,
                        size="6",
                        weight="bold",
                    ),
                    rx.text(title, size="4", weight="medium"),
                    spacing="1",
                    height="100%",
                    align_items="start",
                    width="100%",
                ),
                height="100%",
                spacing="4",
                align="center",
                width="100%",
            ),
            rx.cond(
                trend_text != "",
                rx.hstack(
                    rx.hstack(
                        rx.icon(
                            tag="trending-up" if trend_positive else "trending-down",
                            size=20,
                            color=rx.color("grass" if trend_positive else "tomato", 9),
                        ),
                        rx.text(
                            trend_value,
                            size="3",
                            color=rx.color("grass" if trend_positive else "tomato", 9),
                            weight="medium",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        trend_text,
                        size="2",
                        color=rx.color("gray", 10),
                    ),
                    align="center",
                    width="100%",
                ),
                rx.box(),
            ),
            spacing="3",
        ),
        size="3",
        width="100%",
        box_shadow=styles.box_shadow_style,
    )


def date_range_selector() -> rx.Component:
    """Date range selector component."""
    return rx.hstack(
        rx.text("Year Range:", size="3", weight="medium"),
        rx.select.root(
            rx.select.trigger(placeholder="Start Year"),
            rx.select.content(
                rx.select.item("2017", value="2017"),
                rx.select.item("2018", value="2018"),
                rx.select.item("2019", value="2019"),
                rx.select.item("2020", value="2020"),
                rx.select.item("2021", value="2021"),
                rx.select.item("2022", value="2022"),
                rx.select.item("2023", value="2023"),
                rx.select.item("2024", value="2024"),
                rx.select.item("2025", value="2025"),
            ),
            default_value="2020",
            on_change=ElectrificationDashboardState.set_start_year,
        ),
        rx.text("to", size="2"),
        rx.select.root(
            rx.select.trigger(placeholder="End Year"),
            rx.select.content(
                rx.select.item("2017", value="2017"),
                rx.select.item("2018", value="2018"),
                rx.select.item("2019", value="2019"),
                rx.select.item("2020", value="2020"),
                rx.select.item("2021", value="2021"),
                rx.select.item("2022", value="2022"),
                rx.select.item("2023", value="2023"),
                rx.select.item("2024", value="2024"),
                rx.select.item("2025", value="2025"),
            ),
            default_value="2025",
            on_change=ElectrificationDashboardState.set_end_year,
        ),
        spacing="3",
        align="center",
    )


def chart_type_toggle() -> rx.Component:
    """Toggle between chart types."""
    return rx.hstack(
        rx.text("Chart Type:", size="3", weight="medium"),
        rx.icon_button(
            rx.icon("area-chart"),
            size="2",
            cursor="pointer",
            variant="surface",
            color_scheme=rx.cond(
                ElectrificationDashboardState.chart_type == "area", "blue", "gray"
            ),
            on_click=lambda: ElectrificationDashboardState.set_chart_type("area"),
        ),
        rx.icon_button(
            rx.icon("bar-chart-3"),
            size="2",
            cursor="pointer",
            variant="surface",
            color_scheme=rx.cond(
                ElectrificationDashboardState.chart_type == "bar", "blue", "gray"
            ),
            on_click=lambda: ElectrificationDashboardState.set_chart_type("bar"),
        ),
        spacing="3",
        align="center",
    )


@template(
    route="/",
    title="Electrification Dashboard",
    on_load=ElectrificationDashboardState.load_data,
)
def index() -> rx.Component:
    """The overview page.

    Returns:
        The UI for the overview page.

    """
    return rx.vstack(
        rx.heading(
            "Aotearoa Electrification Progress Tracker", size="7", weight="bold"
        ),
        rx.text(
            "Tracking New Zealand's transition from fossil fuels to electricity",
            size="4",
            color=rx.color("gray", 11),
        ),
        rx.divider(),
        # Date range filter
        rx.hstack(
            date_range_selector(),
            chart_type_toggle(),
            justify="between",
            width="100%",
            padding_y="1em",
        ),
        # KPI Cards
        rx.grid(
            kpi_card(
                title="Electricity Percentage",
                value=f"{ElectrificationDashboardState.latest_electricity_percentage}%",
                icon="zap",
                icon_color="blue",
                trend_text="of total energy consumption",
                trend_value="Current",
                trend_positive=True,
            ),
            kpi_card(
                title="Total Energy Consumption",
                value=f"{ElectrificationDashboardState.total_energy_consumption:,}",
                icon="activity",
                icon_color="green",
                trend_text="GWh in latest month",
                trend_value="Latest",
                trend_positive=True,
            ),
            kpi_card(
                title="New Gas Connections",
                value=f"{ElectrificationDashboardState.total_gas_connections_last_year:,}",
                icon="flame",
                icon_color="orange",
                trend_text="in last 12 months",
                trend_value="Declining",
                trend_positive=False,
            ),
            kpi_card(
                title="Renewable Generation",
                value=f"{ElectrificationDashboardState.avg_renewable_percentage}%",
                icon="leaf",
                icon_color="grass",
                trend_text="average across regions",
                trend_value="Current",
                trend_positive=True,
            ),
            columns="4",
            spacing="4",
            width="100%",
        ),
        # Main content placeholder
        rx.card(
            rx.vstack(
                rx.heading("Dashboard Overview", size="5"),
                rx.text(
                    "Use the navigation menu to explore detailed views of:",
                    size="3",
                ),
                rx.unordered_list(
                    rx.list_item(
                        "Electrification Progress - Track electricity adoption over time"
                    ),
                    rx.list_item(
                        "Energy by Fuel - Analyze energy consumption by fuel type and sector"
                    ),
                    rx.list_item(
                        "Gas Connections - Monitor gas connection trends by region"
                    ),
                    rx.list_item(
                        "Renewable Generation - View renewable energy generation by region"
                    ),
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
