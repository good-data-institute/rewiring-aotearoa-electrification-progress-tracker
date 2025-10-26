# Quick Start Guide - Electrification Dashboard

## Prerequisites
- Python 3.8+
- Reflex installed (`pip install reflex`)

## Running the Dashboard

### 1. Navigate to the Reflex app directory
```bash
cd frontend/reflex_demo
```

### 2. Install dependencies (first time only)
```bash
pip install -r requirements.txt
```

### 3. Initialize Reflex (first time only)
```bash
reflex init
```

### 4. Run the application
```bash
reflex run
```

The dashboard will start and open in your browser at: `http://localhost:3000`

## Dashboard Pages

| Page | URL | Description |
|------|-----|-------------|
| **Overview Dashboard** | `/` | Main dashboard with KPIs for all metrics |
| **Electrification Progress** | `/electrification` | Electricity consumption % over time |
| **Energy by Fuel** | `/energy-fuel` | Energy breakdown by fuel type and sector |
| **Gas Connections** | `/gas-connections` | New gas connections trends by region |
| **Renewable Generation** | `/renewable-generation` | Renewable energy % by region |

## Key Features

### ✅ Implemented
- [x] Load data from 4 CSV sources automatically
- [x] Interactive KPI cards with 4 key metrics
- [x] Date range filtering (2017-2025)
- [x] Chart type toggle (area ↔ bar)
- [x] Interactive charts with hover tooltips
- [x] 5 specialized data visualization pages
- [x] Responsive navigation (sidebar + mobile drawer)
- [x] Color-coded fuel types (clean vs fossil)
- [x] Regional breakdowns for gas and renewable data
- [x] Computed metrics (averages, totals, trends)

### 📊 Visualizations
- **Line/Area Charts:** Time series trends
- **Stacked Charts:** Composition over time
- **Bar Charts:** Categorical comparisons
- **KPI Cards:** Summary metrics with trends

## Data Files Used

The dashboard automatically reads from:
```
data/metrics/
├── eeca/
│   ├── eeca_electricity_percentage.csv
│   └── eeca_energy_by_fuel.csv
├── gic/
│   └── gic_gas_connections_analytics.csv
└── emi_generation/
    └── emi_generation_analytics.csv
```

**Note:** Ensure these files exist in your project before running the dashboard.

## Customization

### Changing the Data Files
Edit `frontend/reflex_demo/reflex_demo/backend/table_state.py`:

```python
# Line ~217: Update paths for your data files
eeca_elec_path = project_root / "data" / "metrics" / "eeca" / "eeca_electricity_percentage.csv"
eeca_fuel_path = project_root / "data" / "metrics" / "eeca" / "eeca_energy_by_fuel.csv"
gic_path = project_root / "data" / "metrics" / "gic" / "gic_gas_connections_analytics.csv"
emi_path = project_root / "data" / "metrics" / "emi_generation" / "emi_generation_analytics.csv"
```

### Changing Default Date Range
Edit `frontend/reflex_demo/reflex_demo/backend/table_state.py`:

```python
# Line ~167-168: Update default years
start_year: int = 2020  # Change to your preferred start year
end_year: int = 2025    # Change to your preferred end year
```

### Changing Colors
Edit individual page files in `frontend/reflex_demo/reflex_demo/pages/`:
- `index.py`: Overview page colors
- `electrification.py`: Electricity chart colors
- `energy_fuel.py`: Fuel type colors
- `gas_connections.py`: Gas chart colors
- `renewable_generation.py`: Renewable chart colors

## Troubleshooting

### Issue: "Module not found" errors
**Solution:** Install Reflex and dependencies
```bash
pip install reflex
pip install -r requirements.txt
```

### Issue: "File not found" errors for CSV files
**Solution:** Verify data files exist at the correct paths
```bash
# From project root
ls data/metrics/eeca/
ls data/metrics/gic/
ls data/metrics/emi_generation/
```

### Issue: Charts not displaying data
**Solution:** Check that CSVs have the expected column names:
- `eeca_electricity_percentage.csv`: Year, Month, _13_P1_ElecCons
- `eeca_energy_by_fuel.csv`: Year, Month, Category, Sub-Category, _14_P1_EnergyxFuel
- `gic_gas_connections_analytics.csv`: Year, Month, Region, _10_P1_Gas
- `emi_generation_analytics.csv`: Year, Month, Region, _12_P1_EnergyRenew

### Issue: Port already in use
**Solution:** Change the port or kill the existing process
```bash
# Change port
reflex run --port 3001

# Or kill existing process (Windows)
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

### Issue: Slow loading
**Solution:** The app loads all CSV files on startup. For large files:
1. Filter data before loading
2. Use pagination for tables
3. Implement lazy loading for charts

## Development Mode

To run in development mode with hot reload:
```bash
reflex run --debug
```

Changes to Python files will automatically reload the app.

## Building for Production

To create a production build:
```bash
reflex export
```

The built files will be in the `.web/_static` directory.

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Support & Documentation

- **Reflex Documentation:** https://reflex.dev/docs/
- **Recharts Documentation:** https://recharts.org/
- **Project Documentation:** See `DASHBOARD_IMPLEMENTATION.md` and `VISUALIZATION_PLAN.md`

## Architecture Summary

```
reflex_demo/
├── reflex_demo/
│   ├── backend/
│   │   └── table_state.py         # Data models & state management
│   ├── components/
│   │   ├── navbar.py              # Mobile navigation
│   │   └── sidebar.py             # Desktop navigation
│   ├── pages/
│   │   ├── index.py               # Overview dashboard
│   │   ├── electrification.py     # Electricity % page
│   │   ├── energy_fuel.py         # Energy by fuel page
│   │   ├── gas_connections.py     # Gas connections page
│   │   └── renewable_generation.py # Renewable gen page
│   └── templates/
│       └── template.py            # Page template wrapper
└── requirements.txt
```

## Quick Commands Reference

```bash
# Navigate to app
cd frontend/reflex_demo

# Run development server
reflex run

# Run with debug mode
reflex run --debug

# Build for production
reflex export

# Clean build files
reflex clean

# Check Reflex version
reflex version
```

## Metrics Displayed

### KPI Cards (Overview)
1. **Electricity Percentage:** Current % of energy from electricity
2. **Total Energy Consumption:** Latest month total in GWh
3. **New Gas Connections:** Last 12 months total
4. **Renewable Generation:** Average % across regions

### Charts
- **Time Series:** Monthly data points (2017-2025)
- **Regional:** Breakdown by NZ regions
- **Sectoral:** By industry/usage sector
- **Fuel Type:** By energy source

## Tips for Best Experience

1. **Desktop:** Use sidebar navigation for quick access
2. **Mobile:** Use hamburger menu for navigation
3. **Charts:** Hover for detailed tooltips
4. **Filters:** Adjust date range to focus on specific periods
5. **Comparison:** Toggle between area and bar charts for different perspectives

## Next Steps

After running the dashboard:
1. Explore each page to understand the data
2. Test the date range filters
3. Experiment with chart type toggles
4. Check mobile responsiveness
5. Review the visualization plan for insights
6. Customize colors/themes as needed
7. Add additional pages for specific analyses

Happy visualizing! 📊🔋⚡
