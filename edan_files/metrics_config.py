metrics_config = [
    # =====================
    # Number of EVs in use
    # =====================
    {
        "metric_id": "_01_P1_EV",
        "filter_conditions": {
            "Fuel_Type": "BEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "BEV",
        "output_name": "01_P1_EV_Private_LPV"
    },
    {
        "metric_id": "_01_P1_EV",
        "filter_conditions": {
            "Fuel_Type": "BEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "BEV",
        "output_name": "01_P1_EV_Commercial_LPV"
    },
    {
        "metric_id": "_01_P1_EV",
        "filter_conditions": {
            "Fuel_Type": "BEV",
            "Category": "Private",
            "Sub_Category": "Bus"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Bus",
        "Fuel_Type": "BEV",
        "output_name": "01_P1_EV_Private_Bus"
    },
    # ==================================
    # Number of fossil fuel cars in use
    # ==================================
    # Light Passenger Vehicle - Private
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "HEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "HEV",
        "output_name": "02_P1_FF_Private_LPV_HEV"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "PHEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "PHEV",
        "output_name": "02_P1_FF_Private_LPV_PHEV"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "FCEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "FCEV",
        "output_name": "02_P1_FF_Private_LPV_FCEV"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "Petrol",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Petrol",
        "output_name": "02_P1_FF_Private_LPV_Petrol"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "Diesel",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Diesel",
        "output_name": "02_P1_FF_Private_LPV_Diesel"
    },
    # Light Passenger Vehicle - Commercial
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "HEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "HEV",
        "output_name": "02_P1_FF_Commercial_LPV_HEV"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "PHEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "PHEV",
        "output_name": "02_P1_FF_Commercial_LPV_PHEV"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "FCEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "FCEV",
        "output_name": "02_P1_FF_Commercial_LPV_FCEV"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "Petrol",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Petrol",
        "output_name": "02_P1_FF_Commercial_LPV_Petrol"
    },
    {
        "metric_id": "_02_P1_FF",
        "filter_conditions": {
            "Fuel_Type": "Diesel",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Diesel",
        "output_name": "02_P1_FF_Commercial_LPV_Diesel"
    },
    # =====================
    # New EVs purchased
    # =====================
    {
        "metric_id": "_03_P1_NewEV",
        "filter_conditions": {
            "Fuel_Type": "BEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "BEV",
        "output_name": "03_P1_NewEV_Private_LPV"
    },
    {
        "metric_id": "_03_P1_NewEV",
        "filter_conditions": {
            "Fuel_Type": "BEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "BEV",
        "output_name": "03_P1_NewEV_Commercial_LPV"
    },
    # =====================
    # New fossil fuel cars purchased
    # =====================
    # Private
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "HEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "HEV",
        "output_name": "04_P1_NewFF_Private_LPV_HEV"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "PHEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "PHEV",
        "output_name": "04_P1_NewFF_Private_LPV_PHEV"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "FCEV",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "FCEV",
        "output_name": "04_P1_NewFF_Private_LPV_FCEV"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "Petrol",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Petrol",
        "output_name": "04_P1_NewFF_Private_LPV_Petrol"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "Diesel",
            "Category": "Private",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Private",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Diesel",
        "output_name": "04_P1_NewFF_Private_LPV_Diesel"
    },
    # Commercial
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "HEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "HEV",
        "output_name": "04_P1_NewFF_Commercial_LPV_HEV"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "PHEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "PHEV",
        "output_name": "04_P1_NewFF_Commercial_LPV_PHEV"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "FCEV",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "FCEV",
        "output_name": "04_P1_NewFF_Commercial_LPV_FCEV"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "Petrol",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Petrol",
        "output_name": "04_P1_NewFF_Commercial_LPV_Petrol"
    },
    {
        "metric_id": "_04_P1_NewFF",
        "filter_conditions": {
            "Fuel_Type": "Diesel",
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle",
            "Condition": "NEW"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": "Diesel",
        "output_name": "04_P1_NewFF_Commercial_LPV_Diesel"
    },
    # =====================
    # % Fleet Electrified
    # =====================
    {
        "metric_id": "_05_P1_Fleet",
        "filter_conditions": {
            "Category": "Commercial",
            "Sub_Category": "Light Passenger Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Passenger Vehicle",
        "Fuel_Type": None,
        "output_name": "05_P1_Fleet_Commercial_LPV",
        "calculation": "percentage_electrified"
    },
    {
        "metric_id": "_05_P1_Fleet",
        "filter_conditions": {
            "Category": "Commercial",
            "Sub_Category": "Light Commercial Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Light Commercial Vehicle",
        "Fuel_Type": None,
        "output_name": "05_P1_Fleet_Commercial_LCV",
        "calculation": "percentage_electrified"
    },
    {
        "metric_id": "_05_P1_Fleet",
        "filter_conditions": {
            "Category": "Commercial",
            "Sub_Category": "Heavy Vehicle"
        },
        "metric_group": "Transport",
        "Category": "Commercial",
        "Sub_Category": "Heavy Vehicle",
        "Fuel_Type": None,
        "output_name": "05_P1_Fleet_Commercial_HV",
        "calculation": "percentage_electrified"
    },
    # Extra metrics for NZ wide aggregation - new BEV vehicles
    # {
    # "metric_id": "_07_P1_Fleet",
    # "filter_conditions": {
    #     "Sub_Category": ["Light Passenger Vehicle", "Light Commercial Vehicle"],
    #     "Condition": "NEW"
    # },
    # "metric_group": "Transport",
    # "Category": "All",
    # "Sub_Category": "Combined Light Fleet",
    # "Fuel_Type": None,
    # "output_name": "07_P1_Fleet_Commercial_Combined_LCV_LPV",
    # "calculation": "percentage_electrified"
    # },
    # {
    # "metric_id": "_07_P1_Fleet",
    # "filter_conditions": {
    #     "Condition": "NEW"
    # },
    # "metric_group": "Transport",
    # "Category": "All",
    # "Sub_Category": "Combined Entire Fleet",
    # "Fuel_Type": None,
    # "output_name": "07_P1_Fleet_Commercial_Combined_All_Vehicles",
    # "calculation": "percentage_electrified"
    # }
]