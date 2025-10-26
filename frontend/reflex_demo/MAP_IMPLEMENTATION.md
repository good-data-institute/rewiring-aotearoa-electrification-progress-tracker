# Map Visualization Implementation

## Overview
This document describes the implementation of interactive map visualizations for the New Zealand Electrification Progress Tracker using Plotly integrated with Reflex.

## What Was Implemented

### 1. Interactive Plotly Maps
- **Renewable Energy Generation Map**: Shows regional renewable energy percentages across NZ regions
- **Gas Connections Map**: Displays gas connection data by region

### 2. Technology Stack
- **Plotly**: For creating interactive geographic scatter plots with markers
- **Reflex `rx.plotly`**: For embedding Plotly figures in the Reflex app
- **Geographic Data**: Scatter geo plots with latitude/longitude coordinates for NZ regions

### 3. Features

#### Renewable Energy Map
- Color-coded markers based on renewable percentage:
  - Dark Green (95-100%): Excellent renewable generation
  - Light Green (80-95%): Good renewable generation
  - Yellow (60-80%): Moderate renewable generation
  - Orange (<60%): Needs improvement
- Marker size varies with renewable percentage (larger = higher percentage)
- Interactive hover tooltips showing region name and exact percentage
- Focused view on New Zealand geography

#### Gas Connections Map
- Color-coded markers based on connection count:
  - Green (<10 connections): Good progress
  - Yellow (10-50 connections): Moderate
  - Orange (50-100 connections): High
  - Red (>100 connections): Very high
- Marker size varies with connection count (larger = more connections)
- Interactive hover tooltips showing region name and connection count
- Focused view on New Zealand geography

### 4. Code Structure

#### Files Modified
1. **`backend/table_state.py`**:
   - Added `plotly.graph_objects` import
   - Added `NZ_REGIONS_COORDS` dictionary with lat/lon coordinates for 30+ NZ regions
   - Added `create_renewable_map_figure()` method to generate renewable energy map
   - Added `create_gas_connections_map_figure()` method to generate gas connections map

2. **`pages/regional_map.py`**:
   - Simplified to use Plotly maps via `rx.plotly()` component
   - Removed non-functional marker-based visualizations
   - Updated `renewable_map()` and `gas_connections_map()` functions
   - Maintained legend components for interpretation

### 5. Data Flow
```
CSV Data → ElectrificationDashboardState (load_data)
    ↓
renewable_generation_by_region_data / gas_connections_by_region_data
    ↓
create_renewable_map_figure() / create_gas_connections_map_figure()
    ↓
Plotly Figure with Scattergeo traces
    ↓
rx.plotly() component renders in browser
```

### 6. Region Coordinates
The implementation includes geographic coordinates (latitude/longitude) for 30+ NZ regions:
- Major regions: Auckland, Wellington, Canterbury, Otago, etc.
- Sub-regions: Bay of Islands, Central Canterbury, Dunedin, Rotorua, etc.

## Usage

### Running the App
```bash
cd frontend/reflex_demo
reflex run
```

Navigate to the "Regional Map" page to view the interactive maps.

### Viewing the Maps
1. Click on the "Regional Map" tab in the navigation
2. Switch between tabs:
   - **Renewable Generation**: View renewable energy performance
   - **Gas Connections**: View gas connection trends
   - **Comparison Table**: View tabular data comparison

### Interacting with Maps
- **Hover**: Over markers to see detailed information
- **Zoom**: Use mouse wheel or pinch gesture
- **Pan**: Click and drag to move around the map
- **Color Scale**: Reference the color bar on the right side

## Technical Details

### Plotly Scattergeo Configuration
- **Projection**: Mercator
- **Center**: Longitude 173°, Latitude -41° (NZ center)
- **Scale**: 15x zoom for NZ focus
- **Map Features**: Land, coastlines, lakes visible

### Color Scales
- **Renewable**: Orange → Yellow → Light Green → Dark Green
- **Gas**: Green → Yellow → Orange → Red

### Data Aggregation
- Renewable data: Averaged across filtered time period
- Gas data: Latest year's total connections per region

## Future Enhancements

Potential improvements:
1. Add temporal animation showing changes over time
2. Include choropleth maps with actual NZ regional boundaries
3. Add filtering controls directly on the map page
4. Include additional metrics (electricity consumption, etc.)
5. Add export functionality for map images
6. Implement region selection to filter other dashboard views

## Dependencies
- `plotly`: Already installed in the project
- No additional dependencies required

## Notes
- The implementation uses scatter geo plots rather than choropleth because we don't have GeoJSON boundary data for NZ regions
- Coordinates are approximate centroids of each region
- This is a working proof-of-concept that can be enhanced with more precise geographic data
