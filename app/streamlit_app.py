import os
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000/predict")

st.set_page_config(
    page_title="UK Road Accident Severity",
    page_icon="🚗",
    layout="wide",
)

st.title("UK Road Accident Severity Prediction")
st.caption("Explore collision severity using road, vehicle and casualty information.")


OPTIONS = {
    "road_type": {
        None: "Not provided",
        1: "Roundabout",
        2: "One-way road",
        3: "Divided road",
        6: "Undivided road",
        7: "Slip road",
    },
    "weather_conditions": {
        None: "Not provided",
        1: "Fine weather, no strong wind",
        2: "Rain, no strong wind",
        3: "Snow, no strong wind",
        4: "Fine weather, strong wind",
        5: "Rain and strong wind",
        6: "Snow and strong wind",
        7: "Fog or mist",
        8: "Other weather",
        9: "Recorded as unknown",
    },
    "light_conditions": {
        None: "Not provided",
        1: "Daytime",
        4: "Night, street lighting on",
        5: "Night, street lighting off",
        6: "Night, no street lighting",
        7: "Night, lighting unknown",
    },
    "road_surface_conditions": {
        None: "Not provided",
        1: "Dry surface",
        2: "Wet surface",
        3: "Snow-covered surface",
        4: "Ice or frost",
        5: "Flooded surface",
    },
    "most_common_vehicle_type": {
        None: "Not provided",
        1: "Bicycle",
        8: "Taxi or private hire",
        9: "Car",
        11: "Bus or coach",
        19: "Goods vehicle up to 3.5 tonnes",
        20: "Goods vehicle over 3.5 to 7.5 tonnes",
        21: "Goods vehicle over 7.5 tonnes",
    },
}

LABELS = {
    "road_type": "Road type",
    "weather_conditions": "Weather",
    "light_conditions": "Lighting",
    "road_surface_conditions": "Road surface",
    "most_common_vehicle_type": "Most common vehicle type",
}

AGE_FIELDS = {
    "average_driver_age": "Average driver age",
    "average_vehicle_age": "Average vehicle age",
    "max_vehicle_age": "Oldest vehicle age",
    "average_casualty_age": "Average casualty age",
    "max_casualty_age": "Oldest casualty age",
}

LOCATION_FIELDS = {
    "longitude": "Longitude",
    "latitude": "Latitude",
    "location_easting_osgr": "OS grid easting",
    "location_northing_osgr": "OS grid northing",
}

CODE_FIELDS = {
    "police_force": "Police force",
    "local_authority_district": "Local authority district",
    "first_road_class": "First road class",
    "second_road_class": "Second road class",
    "junction_detail": "Junction detail",
    "junction_control": "Junction control",
    "pedestrian_crossing": "Pedestrian crossing",
    "special_conditions_at_site": "Special site conditions",
    "carriageway_hazards": "Carriageway hazards",
    "urban_or_rural_area": "Urban or rural area",
    "did_police_officer_attend_scene_of_accident": "Police attendance",
    "trunk_road_flag": "Trunk road flag",
}

SEVERITY_LABELS = {
    "1": "Fatal",
    "2": "Serious",
    "3": "Slight",
}


with st.form("prediction_form"):
    features = {}

    st.subheader("Collision details")
    columns = st.columns(3)

    with columns[0]:
        collision_date = st.date_input("Date", value=None)
        collision_time = st.time_input("Time", value=None)

    with columns[1]:
        features["number_of_vehicles"] = st.number_input(
            "Number of vehicles",
            min_value=1,
            value=None,
            step=1,
        )
        features["number_of_casualties"] = st.number_input(
            "Number of casualties",
            min_value=1,
            value=None,
            step=1,
        )

    with columns[2]:
        features["speed_limit"] = st.number_input(
            "Speed limit (mph)",
            min_value=1,
            value=None,
            step=1,
        )

    st.subheader("Road and conditions")
    columns = st.columns(3)

    for index, (field, options) in enumerate(OPTIONS.items()):
        with columns[index % 3]:
            features[field] = st.selectbox(
                LABELS[field],
                options=list(options),
                format_func=lambda code, labels=options: labels[code],
            )

    with st.expander("Driver, vehicle and casualty ages"):
        columns = st.columns(3)

        for index, (field, label) in enumerate(AGE_FIELDS.items()):
            with columns[index % 3]:
                features[field] = st.number_input(
                    f"{label} (years)",
                    min_value=0.0,
                    value=None,
                    step=1.0,
                    key=field,
                )

    with st.expander("Location"):
        columns = st.columns(2)

        for index, (field, label) in enumerate(LOCATION_FIELDS.items()):
            with columns[index % 2]:
                features[field] = st.number_input(
                    label,
                    value=None,
                    format="%.6f",
                    key=field,
                )

    with st.expander("Additional recorded details"):
        st.caption(
            "Optional STATS19 codes. Leave blank when the code is not known."
        )
        columns = st.columns(3)

        for index, (field, label) in enumerate(CODE_FIELDS.items()):
            with columns[index % 3]:
                features[field] = st.number_input(
                    label,
                    value=None,
                    step=1,
                    key=field,
                )

    submitted = st.form_submit_button(
        "Predict severity",
        type="primary",
        use_container_width=True,
    )


if submitted:
    required_values = [
        collision_date,
        collision_time,
        features["number_of_vehicles"],
        features["number_of_casualties"],
        features["speed_limit"],
    ]

    if any(value is None for value in required_values):
        st.error("Enter the date, time, vehicle count, casualty count and speed limit.")
    else:
        features.update({
            "collision_year": collision_date.year,
            "month": collision_date.month,
            "day": collision_date.day,
            "day_of_week": (collision_date.weekday() + 1) % 7 + 1,
            "hour": collision_time.hour,
        })

        try:
            with st.spinner("Generating prediction..."):
                response = requests.post(
                    API_URL,
                    json={"features": features},
                    timeout=30,
                )

            if response.status_code != 200:
                st.error("The API could not process the prediction.")
                st.json(response.json())
            else:
                result = response.json()
                severity = str(result["severity_code"])

                st.divider()
                st.subheader("Prediction")
                st.metric(
                    "Predicted severity",
                    SEVERITY_LABELS[severity],
                )

                columns = st.columns(3)

                for column, code in zip(columns, SEVERITY_LABELS):
                    probability = result["probabilities"][code]

                    with column:
                        st.metric(
                            SEVERITY_LABELS[code],
                            f"{probability:.1%}",
                        )
                        st.progress(float(probability))

                st.caption(
                    "Model class probabilities are not calibrated risk estimates."
                )

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the prediction API.")
        except requests.exceptions.Timeout:
            st.error("The prediction request timed out.")