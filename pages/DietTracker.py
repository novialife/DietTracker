import streamlit as st
import pandas as pd
import plotly.express as px
from db import read_data, save_data

st.set_page_config(layout="wide")

age, height, activity_level, info = st.columns(4)
with age:
    AGE = st.selectbox("Age", options=list(range(18, 101)), key="age", index=5)
with height:
    HEIGHT = st.selectbox(
        "Height (cm)", options=list(range(140, 221)), key="height", index=43
    )
with activity_level:
    ACTIVITY_LEVEL = st.selectbox(
        "Activity Level",
        options=[
            "Sedentary",
            "Lightly Active",
            "Moderately Active",
            "Very Active",
            "Extra Active",
        ],
        key="activity_level",
    )
    if ACTIVITY_LEVEL == "Sedentary":
        ACTIVITY_LEVEL = 1.2
    elif ACTIVITY_LEVEL == "Lightly Active":
        ACTIVITY_LEVEL = 1.375
    elif ACTIVITY_LEVEL == "Moderately Active":
        ACTIVITY_LEVEL = 1.55
    elif ACTIVITY_LEVEL == "Very Active":
        ACTIVITY_LEVEL = 1.725
    elif ACTIVITY_LEVEL == "Extra Active":
        ACTIVITY_LEVEL = 1.9
with info:
    st.markdown("Hover over the button to see the help text", unsafe_allow_html=True)
    st.button(
        "Activity Level Descriptions",
        disabled=True,
        help="Sedentary (little or no exercise)\n\nLightly Active (light exercise/sports 1-3 days/week)\n\nModerately Active (moderate exercise/sports 3-5 days/week)\n\nVery Active (hard exercise/sports 6-7 days a week)\n\nExtra Active (very hard exercise/sports & physical job or 2x training)",
    )


def mifflin_st_joer(weight):
    return (10 * weight) + (6.25 * HEIGHT) - (5 * AGE) + 5


# Placeholder function for nutritional calculation
def calculate_nutrition(selected_option, food_data):
    food = food_data[food_data["description"] == selected_option]
    cols = [
        "Carbohydrate, by difference",
        "Energy (kcal)",
        "Protein",
        "Total lipid (fat)",
    ]
    nutrition = food[cols].values[0]
    return {
        "carbs": nutrition[0],
        "calories": nutrition[1],
        "protein": nutrition[2],
        "fat": nutrition[3],
    }


def exercise_tracker(exercise_records, exercise_day):
    exercise_name = st.text_input(
        f"Exercise Name ({exercise_day})", key=f"name_{exercise_day}"
    )
    weight_lifted = st.number_input(
        "Weight Lifted (kg)", min_value=0.0, key=f"weight_{exercise_day}"
    )
    reps_done = st.number_input("Reps", min_value=0, key=f"reps_{exercise_day}")
    sets_done = st.number_input("Sets", min_value=0, key=f"sets_{exercise_day}")
    add_exercise = st.button(
        f"Add Exercise ({exercise_day})", key=f"add_{exercise_day}"
    )
    if add_exercise and exercise_name:
        new_exercise = pd.DataFrame(
            {
                "Date": [pd.to_datetime("today").date()],
                "Day": [exercise_day],
                "Exercise Name": [exercise_name],
                "Weight Lifted": [weight_lifted],
                "Reps": [reps_done],
                "Sets": [sets_done],
                "Volume": [weight_lifted * reps_done * sets_done],
            }
        )
        save_data(new_exercise, "cut.db", exercise_day)
        st.rerun()

    filtered_records = exercise_records[exercise_records["Day"] == exercise_day]
    if not filtered_records.empty:
        exercise_names = filtered_records["Exercise Name"].unique()
        selected_exercise = st.selectbox(
            f"Select Exercise ({exercise_day})", options=exercise_names
        )
        if selected_exercise:
            specific_exercise_records = filtered_records[
                filtered_records["Exercise Name"] == selected_exercise
            ]
            # Group by date and sum the volume for each day
            specific_exercise_records = (
                specific_exercise_records.groupby("Date").sum().reset_index()
            )
            fig = px.line(
                specific_exercise_records,
                x="Date",
                y="Volume",
                title=f"Volume Over Time: {selected_exercise}",
            )
            st.plotly_chart(fig)


def main():
    st.title("Diet and Exercise Tracker")

    # Bodyweight Tracker
    st.header("Bodyweight Tracker")
    bodyweight_records = read_data("cut.db", "Bodyweight")[["Date", "Weight", "BMR"]]

    date = st.date_input("Date")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    submit_weight = st.button("Record Weight")

    if (
        submit_weight
        and pd.to_datetime("today").date() not in bodyweight_records["Date"].values
    ):
        new_record = pd.DataFrame(
            {
                "Date": [date],
                "Weight": [weight],
                "BMR": [int(mifflin_st_joer(weight) * ACTIVITY_LEVEL)],
            }
        )

        save_data(new_record, "cut.db", "Bodyweight")

    bw = read_data("cut.db", "Bodyweight")
    st.dataframe(bw, use_container_width=True)

    weight_graph, bmr_graph = st.columns(2)
    with weight_graph:
        fig = px.line(
            bodyweight_records, x="Date", y="Weight", title="Weight Over Time"
        )
        st.plotly_chart(fig)

    with bmr_graph:
        fig = px.line(bodyweight_records, x="Date", y="BMR", title="BMR Over Time")
        st.plotly_chart(fig)

    st.header("Gym Exercises Tracker")
    tab_leg, tab_back, tab_chest = st.tabs(["Leg Day", "Back Day", "Chest Day"])

    days = ["Leg Day", "Back Day", "Chest Day"]
    tabs = [tab_leg, tab_back, tab_chest]
    for tab, day in zip(tabs, days):
        with tab:
            st.subheader(day)
            exercise_records = read_data("cut.db", day)
            exercise_tracker(exercise_records, day)

    default_food, custom_food = st.columns(2)
    with default_food:
        # Food Tracker
        st.header("Food Tracker")

        # User input text box
        user_input = st.text_input("Search for a food item:", "")

        # Filtering the dataframe based on the user input
        food_data = read_data("food.db", "Foods")
        filtered_df = food_data[
            food_data["description"].str.contains(user_input, case=False, na=False)
        ]

        # Creating a list of options to display in the dropdown
        # Ensuring the list is unique and sorted
        options = sorted(filtered_df["description"].unique())

        # Displaying the dropdown menu with the available options
        selected_option = st.selectbox("Select a food item:", options)

        # Placeholder for quantity input
        quantity = st.number_input("Quantity (grams)", min_value=0)

        # Placeholder for adding the food item to the tracker
        add_food = st.button("Add Food Item")

        if add_food:
            nutrition = calculate_nutrition(selected_option, food_data)
            new_food = pd.DataFrame(
                {
                    "Date": [date],
                    "Food Item": [selected_option],
                    "Quantity": [quantity],
                    "Calories": [nutrition["calories"] * quantity / 100],
                    "Fat": [nutrition["fat"] * quantity / 100],
                    "Protein": [nutrition["protein"] * quantity / 100],
                    "Carbohydrates": [nutrition["carbs"] * quantity / 100],
                }
            )

            save_data(new_food, "food.db", "Food Tracker")

    with custom_food:
        # Custom Food Tracker
        st.header("Custom Food")
        with st.expander("Add Custom Food"):
            custom_food_name = st.text_input("Food Name")
            custom_calories = st.number_input("Calories (kcal per 100g)", min_value=0)
            custom_protein = st.number_input("Protein (g per 100g)", min_value=0.0)
            custom_fat = st.number_input("Fat (g per 100g)", min_value=0.0)
            custom_carbs = st.number_input("Carbohydrates (g per 100g)", min_value=0.0)
            add_custom_food = st.button("Add Custom Food")

            if add_custom_food:
                new_custom_food = pd.DataFrame(
                    {
                        "description": [custom_food_name],
                        "Energy (kcal)": [custom_calories],
                        "Protein": [custom_protein],
                        "Total lipid (fat)": [custom_fat],
                        "Carbohydrate, by difference": [custom_carbs],
                    }
                )
                # Save the new custom food data correctly by specifying the file path
                save_data(new_custom_food, "food.db", "Foods")
                st.success(f"Custom food '{custom_food_name}' added successfully!")

    data = read_data("food.db", "Food Tracker")
    st.dataframe(data.sort_values(by="Date"), use_container_width=True)

    cals, protein, fat, carbs = st.columns(4)
    with cals:
        today = (data.loc[data["Date"] == date.strftime("%Y-%m-%d"), "Calories"].sum()).round(2)
        yesterday = data.loc[data["Date"] == (date - pd.Timedelta(days=1)).strftime("%Y-%m-%d"), "Calories"].sum()
        delta = (today - yesterday).round(2)
        st.metric(label="Today's Calories", value=today, delta=delta)
    with protein:
        today = (data.loc[data["Date"] == date.strftime("%Y-%m-%d"), "Protein"].sum()).round(2)
        yesterday = data.loc[data["Date"] == (date - pd.Timedelta(days=1)).strftime("%Y-%m-%d"), "Protein"].sum()
        delta = (today - yesterday).round(2)
        st.metric(label="Today's Protein", value=today, delta=delta)
    with fat:
        today = (data.loc[data["Date"] == date.strftime("%Y-%m-%d"), "Fat"].sum()).round(2)
        yesterday = data.loc[data["Date"] == (date - pd.Timedelta(days=1)).strftime("%Y-%m-%d"), "Fat"].sum()
        delta = (today - yesterday).round(2)
        st.metric(label="Today's Fat", value=today, delta=delta)
    with carbs:
        today = (data.loc[data["Date"] == date.strftime("%Y-%m-%d"), "Carbohydrates"].sum()).round(2)
        yesterday = data.loc[data["Date"] == (date - pd.Timedelta(days=1)).strftime("%Y-%m-%d"), "Carbohydrates"].sum()
        delta = (today - yesterday).round(2)
        st.metric(label="Today's Carbohydrates", value=today, delta=delta)

    # Sum the calories column for each day and display a graph
    plot_data = data.groupby("Date").sum().reset_index()
    fig = px.line(plot_data, x="Date", y="Calories", title="Calories Over Time")
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
