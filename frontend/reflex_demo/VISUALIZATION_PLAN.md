# Electrification Dashboard - Visualization Plan

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                  AOTEAROA ELECTRIFICATION PROGRESS              │
│                        TRACKER DASHBOARD                         │
├─────────────────────────────────────────────────────────────────┤
│  Filters: [Start Year ▼] to [End Year ▼]  [Area ⬚] [Bar ▢]   │
├──────────────┬──────────────┬──────────────┬──────────────────┤
│   ⚡ 25.5%   │  📊 500,000  │   🔥 2,500   │   🌿 92.3%      │
│ Electricity  │   Energy     │     Gas      │   Renewable      │
│ Percentage   │ Consumption  │  Connections │  Generation      │
├──────────────┴──────────────┴──────────────┴──────────────────┤
│                     NAVIGATION GUIDE                            │
│  • Electrification Progress - Track electricity adoption       │
│  • Energy by Fuel - Analyze by fuel type and sector           │
│  • Gas Connections - Monitor gas trends by region             │
│  • Renewable Generation - View renewable energy by region     │
└─────────────────────────────────────────────────────────────────┘
```

## Page 1: Electrification Progress (`/electrification`)

### Main Visualization
**Chart Type:** Area Chart (toggle to Line)
**Data Source:** EECA Electricity Percentage
**X-Axis:** Time (2017-2023, monthly)
**Y-Axis:** Percentage (0-100%)
**Line Color:** Blue (#3b82f6)

```
Electricity %
    26 ┤                                    ╱─────
       │                              ╱────╯
    25 ┤                        ╱────╯
       │                  ╱────╯
    24 ┤            ╱────╯
       │      ╱────╯
    23 ┤╱────╯
       └────────────────────────────────────────── Time
      2017  2018  2019  2020  2021  2022  2023
```

**Insights:**
- Shows steady increase from ~24% to ~25.5%
- Indicates gradual electrification progress
- Badge shows current percentage

---

## Page 2: Energy by Fuel (`/energy-fuel`)

### Visualization 1: Stacked Area/Bar Chart
**Data Source:** EECA Energy by Fuel
**Aggregation:** By fuel type over time
**Chart Types:** Toggle between Stacked Area and Stacked Bar

**Fuel Types & Colors:**
- 🔵 **Electricity** (Blue #3b82f6) - Clean energy
- ⚫ **Coal** (Gray #6b7280) - Fossil fuel
- 🟠 **Diesel** (Orange #f97316) - Fossil fuel
- 🔴 **Petrol** (Red #ef4444) - Fossil fuel
- 🟤 **Wood** (Brown #92400e) - Biomass
- 🟣 **Other** (Purple #9333ea) - Mixed

```
Energy (GWh)
 500K ┤██████████████████████████████████  Other
      │██████████████████████████████████  Petrol
 400K ┤██████████████████████████████████  Diesel
      │██████████████████████████████████  Wood
 300K ┤██████████████████████████████████  Coal
      │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  Electricity
 200K ┤▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
      │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 100K ┤▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
      └────────────────────────────────── Time
     2017  2018  2019  2020  2021  2022  2023
```

**Insights:**
- Bottom blue section (electricity) should grow over time
- Fossil fuel layers (coal, diesel, petrol) should shrink
- Total height shows total energy consumption

### Visualization 2: Energy by Sector
**Chart Type:** Grouped Bar Chart
**Sectors:**
- 🌾 Agriculture, Forestry & Fishing (Green)
- 🏢 Commercial (Blue)
- 🏭 Industrial (Orange)
- 🏠 Residential (Purple)
- 🚗 Transport (Red)

---

## Page 3: Gas Connections (`/gas-connections`)

### Visualization 1: Trend Over Time
**Chart Type:** Line Chart
**Data Source:** GIC Gas Connections
**X-Axis:** Time (2020-2025, monthly)
**Y-Axis:** New Connections
**Line Color:** Orange (#f97316)

```
Connections
 600 ┤╲
     │ ╲
 500 ┤  ╲___
     │      ╲___
 400 ┤          ╲___
     │              ╲___
 300 ┤                  ╲___
     │                      ╲___
 200 ┤                          ╲___
     └────────────────────────────────── Time
    2020    2021    2022    2023   2024  2025
```

**Insights:**
- Declining trend = good for electrification
- Shows shift away from gas infrastructure
- Lower connections indicate fossil fuel phase-out

### Visualization 2: Regional Breakdown
**Chart Type:** Horizontal Bar Chart
**Regions:** Auckland, Wellington, Canterbury, etc.
**Color:** Orange gradient

```
Auckland     ████████████████████████░░░  2,400
Wellington   ████████████████░░░░░░░░░░░    800
Canterbury   ██████████░░░░░░░░░░░░░░░░░    500
Waikato      ████████░░░░░░░░░░░░░░░░░░░    400
Taranaki     ██░░░░░░░░░░░░░░░░░░░░░░░░░    100
```

---

## Page 4: Renewable Generation (`/renewable-generation`)

### Main Visualization
**Chart Type:** Bar Chart
**Data Source:** EMI Generation Analytics
**X-Axis:** Regions (rotated labels)
**Y-Axis:** Renewable % (0-100%)
**Color:** Green gradient (#22c55e)

```
Renewable %
    100 ┤███ ███ ███ ███ ███ ███     ███ ███
        │███ ███ ███ ███ ███ ███     ███ ███
     90 ┤███ ███ ███ ███ ███ ███  ██ ███ ███
        │███ ███ ███ ███ ███ ███  ██ ███ ███
     80 ┤███ ███ ███ ███ ███ ███  ██ ███ ███
        │███ ███ ███ ███ ███ ███  ██ ███ ███
     70 ┤███ ███ ███ ███ ███ ███  ██ ███ ███
        └─────────────────────────────────────
         A   B   C   D   W   T   U   G   M
         u   a   e   u   a   a   n   i   a
         c   y   n   n   i   r   k   s   n
         k   o   t   e   k   a   n   b   a
         l   f   r   d   a   n   o   o   w
         a   P   a   i   t   a   w   r   a
         n   l   l   n   o   k   n   n   t
         d   e       .       i           e   u
             n
             t
             y
```

**Insights:**
- Most regions should show high % (near 100%)
- Lower percentages indicate areas for improvement
- Goal: 100% renewable by 2030

### Summary Card
Large KPI display:
```
┌─────────────────────────────┐
│      🌿  92.3%             │
│  Average Renewable          │
│     Generation              │
└─────────────────────────────┘
```

---

## Color Palette Summary

### Energy Sources
- **Clean/Renewable:** Blue, Green, Grass tones
- **Fossil Fuels:** Orange, Red, Gray tones
- **Biomass:** Brown tones

### Status Indicators
- **Positive Trends:** Green (#22c55e)
- **Negative Trends:** Red (#ef4444)
- **Neutral:** Blue (#3b82f6)

### UI Elements
- **Primary Actions:** Blue
- **Warnings:** Orange
- **Success:** Green
- **Info:** Cyan

---

## Interactive Features

### Hover Tooltips
All charts include interactive tooltips showing:
- **Date/Period:** Exact time point
- **Value:** Precise number with units
- **Context:** Additional relevant information

Example tooltip:
```
┌──────────────────────┐
│ Date: 2023-06       │
│ Electricity: 25.5%  │
│ Trend: ↑ 0.3%       │
└──────────────────────┘
```

### Chart Type Toggle
Users can switch between:
- **Area Charts:** Show trends with filled regions (better for proportions)
- **Bar Charts:** Show discrete values (better for comparisons)

### Date Range Filter
```
Year Range: [2020 ▼] to [2025 ▼]
```
- Applies to all visualizations
- Default: 2020-2025 (focus on recent trends)
- Available: 2009-2025 (full historical data)

### Regional Filter
```
Filter by Region:
☐ Auckland
☐ Wellington
☐ Canterbury
☐ Waikato
☐ ... (all regions)
```
- Applies to gas connections and renewable generation
- Allows multi-select
- Default: All regions

---

## Responsive Design

### Desktop (>1024px)
- Sidebar navigation (always visible)
- Full-width charts
- Grid layout for KPI cards (4 columns)

### Tablet (768px - 1024px)
- Collapsible sidebar
- Adjusted chart heights
- Grid layout for KPI cards (2 columns)

### Mobile (<768px)
- Drawer menu navigation
- Stacked charts
- Single column layout
- Scrollable tables

---

## Accessibility Features

1. **Color Blind Friendly:** Uses patterns in addition to colors
2. **Keyboard Navigation:** All interactive elements accessible via keyboard
3. **Screen Reader Support:** Proper ARIA labels
4. **High Contrast Mode:** Compatible with system preferences
5. **Readable Fonts:** Minimum 14px for body text

---

## Performance Considerations

1. **Data Loading:** All CSVs loaded once on initialization
2. **Computed Properties:** Cached using `@rx.var(cache=True)`
3. **Filtering:** Client-side for instant updates
4. **Chart Rendering:** Recharts library (optimized React components)
5. **Responsive Images:** No large images, vector-based charts

---

## Next Steps for Testing

1. Run `reflex run` in the `frontend/reflex_demo` directory
2. Navigate to `http://localhost:3000`
3. Verify all pages load
4. Test chart interactions (hover, toggle)
5. Test filters (date range, regions)
6. Check mobile responsiveness
7. Verify data accuracy against CSV files
