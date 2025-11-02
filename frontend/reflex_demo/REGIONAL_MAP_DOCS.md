# Regional Map Visualization

## Overview
An interactive map-based visualization showing renewable generation and gas connections across New Zealand regions.

## Features

### 1. Interactive Regional Map
- **Visual Representation**: Regions displayed as circles on a map layout
- **Hover Tooltips**: Detailed information on hover
- **Color Coding**: Performance-based color gradients
- **Size Scaling**: Circle size represents metric values

### 2. Two Map Views

#### Renewable Generation Map
**Purpose**: Show renewable energy percentage by region

**Visual Encoding:**
- **Circle Size**: Proportional to renewable percentage (30-60px)
- **Colors**:
  - 🟢 Dark Green (`grass-9`): 95-100% renewable (Excellent)
  - 🟢 Green (`grass-7`): 80-95% renewable (Good)
  - 🟡 Yellow (`yellow-7`): 60-80% renewable (Fair)
  - 🟠 Orange (`orange-7`): <60% renewable (Needs Improvement)

**Interpretation:**
- Larger, darker green circles = Better performance
- Most NZ regions should show dark green (high renewable generation)

#### Gas Connections Map
**Purpose**: Show new gas connections by region (latest year)

**Visual Encoding:**
- **Circle Size**: Proportional to number of connections (25-55px)
- **Colors**:
  - 🔴 Red (`red-7`): >100 connections (High fossil fuel adoption)
  - 🟠 Orange (`orange-7`): 50-100 connections (Moderate)
  - 🟡 Yellow (`yellow-7`): 10-50 connections (Low)
  - 🟢 Green (`grass-7`): <10 connections (Excellent for electrification!)

**Interpretation:**
- Smaller, greener circles = Better for electrification
- Declining connections indicate shift away from gas

### 3. Regional Layout

Approximate positioning of NZ regions on the map:

```
         North Island
    ┌─────────────────┐
    │   Northland     │  (Top)
    │                 │
    │    Auckland     │
    │                 │
    │  Waikato  Bay   │
    │          of     │
    │        Plenty   │ Gisborne
    │                 │
    │  Taranaki       │ Hawkes Bay
    │         Manawatu│
    │  Wanganui       │
    │    Wellington   │
    └─────────────────┘

         South Island
    ┌─────────────────┐
    │ Tasman Marlboro │
    │                 │
    │  West Coast     │
    │                 │
    │   Canterbury    │
    │                 │
    │     Otago       │
    │                 │
    │   Southland     │
    └─────────────────┘
```

### 4. Tab Navigation

**Three Tabs:**
1. **Renewable Generation Tab**: Interactive map of renewable %
2. **Gas Connections Tab**: Interactive map of gas connections
3. **Comparison Table Tab**: Side-by-side data table

### 5. Comparison Table

Shows:
- Region name
- Renewable % (color-coded badge)
- Gas connections (latest year)
- Overall status (Excellent/Good/Needs Improvement)

## Regional Coordinates

Regions positioned using absolute positioning with approximate NZ geography:

| Region | Top | Left | Description |
|--------|-----|------|-------------|
| Northland | 5% | 45% | Far north |
| Auckland | 15% | 45% | Upper North Island |
| Waikato | 25% | 45% | Central North Island |
| Bay of Plenty | 25% | 60% | East coast |
| Gisborne | 30% | 70% | Easternmost |
| Hawkes Bay | 40% | 65% | East coast mid |
| Taranaki | 40% | 35% | West coast |
| Manawatu | 50% | 45% | Central lower NI |
| Wanganui | 48% | 40% | West coast lower |
| Wellington | 60% | 50% | Southern tip NI |
| Tasman | 55% | 55% | Top South Island |
| Marlborough | 58% | 62% | NE South Island |
| West Coast | 65% | 50% | West SI |
| Canterbury | 72% | 55% | Central SI |
| Otago | 82% | 55% | Southern SI |
| Southland | 92% | 52% | Bottom SI |

## How to Use

### For Users:
1. Navigate to "Regional Map" in the sidebar/menu
2. Select a tab (Renewable/Gas/Table)
3. Hover over region circles to see details
4. Compare regions visually by size and color

### For Developers:
The map uses:
- `rx.box` with absolute positioning for regional markers
- `rx.foreach` to iterate over regional data
- `rx.tooltip` for hover information
- `rx.tabs` for view switching
- Color scheme from Reflex's built-in color system

## Data Sources

- **Renewable Generation**: From EMI generation analytics CSV
  - Aggregated average by region
  - Filtered by selected date range

- **Gas Connections**: From GIC gas connections CSV
  - Latest year data only
  - Sum of all connections per region

## Design Decisions

### Why Circles Instead of Actual Map?
1. **Simplicity**: No external mapping libraries needed
2. **Performance**: Fast rendering with pure Reflex components
3. **Accessibility**: Clear visual hierarchy
4. **Interactivity**: Easy tooltip implementation
5. **Reflex-only Requirement**: Uses only built-in components

### Why This Layout?
- Approximates NZ geography for familiar reference
- Prevents overlap with strategic spacing
- Works on mobile (relative positioning)
- Scalable for different screen sizes

## Enhancements (Future)

If using external libraries becomes an option:
- [ ] Actual GeoJSON map with proper boundaries
- [ ] Chloropleth coloring on regions
- [ ] Zoom and pan functionality
- [ ] Time-based animation
- [ ] Click-through to detailed regional pages

## Technical Implementation

### Key Components:

**region_marker()**: Creates a positioned circle with:
- Dynamic size based on value
- Color based on performance
- Hover tooltip with details
- Smooth hover animation

**renewable_map()**: Container with:
- Gray background
- Absolute positioned markers
- Legend for interpretation

**gas_connections_map()**: Similar to renewable map but:
- Different color scheme
- Inverted "good" interpretation

**regional_comparison_table()**: Data table with:
- Sortable columns
- Color-coded badges
- Status indicators

## Color Accessibility

Colors chosen for:
- Color-blind friendliness (green/red not sole differentiator)
- High contrast for readability
- Consistent with dashboard theme
- Semantic meaning (green=good, red=warning)

## Mobile Responsiveness

- Circles scale down on smaller screens
- Tabs stack vertically on mobile
- Table scrolls horizontally if needed
- Touch-friendly hover (tap to see tooltip)

## Performance Notes

- No external API calls
- All data pre-loaded in state
- Efficient rendering with Reflex
- Minimal re-renders with cached computed properties

## Integration with Dashboard

The Regional Map page:
- Uses same state (`ElectrificationDashboardState`)
- Respects date range filters
- Shares color scheme with other pages
- Maintains consistent navigation
- Complements other visualizations

## Usage Tips

1. **Compare Regions**: Use the map to quickly spot high/low performers
2. **Track Progress**: Lower gas connections + higher renewable = success
3. **Identify Priorities**: Focus on orange/red regions for improvement
4. **Validate Data**: Cross-reference with table view
5. **Share Insights**: Visual format great for presentations

---

**Page Route**: `/regional-map`
**Title**: "Regional Map"
**Icon**: Map (📍)
**Order**: 6th in navigation (after Renewable Generation, before Table)
