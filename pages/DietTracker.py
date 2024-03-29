import streamlit as st
import pandas as pd
import plotly.express as px
from db import read_data, save_data, delete

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
        index=2,
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
        save_data(new_exercise, "tim.db", exercise_day)
        st.rerun()

    filtered_records = exercise_records[exercise_records["Day"] == exercise_day]
    if not filtered_records.empty:
        exercise_names = filtered_records["Exercise Name"].unique()
        # Plot all exercises grouped by the date and summed by the volume in separate graphs
        for exercise in exercise_names:
            exercise_data = filtered_records[filtered_records["Exercise Name"] == exercise]
            # Group by date and sum the volume
            exercise_data = exercise_data.groupby("Date")["Volume"].sum().reset_index()
            fig = px.line(
                exercise_data, x="Date", y="Volume", title=f"{exercise} Volume Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)



def main():
    st.title("Diet and Exercise Tracker")

    # Bodyweight Tracker
    st.header("Bodyweight Tracker")
    bodyweight_records = read_data("tim.db", "Bodyweight")[["Date", "Weight", "BMR"]]

    # Record weight section
    date = st.date_input("Date")
    weight = st.number_input("Weight (kg)", min_value=0.0)
    submit_weight = st.button("Record Weight")

    if submit_weight and pd.to_datetime("today").date() not in bodyweight_records["Date"].values:
        new_record = pd.DataFrame(
            {
                "Date": [date],
                "Weight": [weight],
                "BMR": [int(mifflin_st_joer(weight) * ACTIVITY_LEVEL)],
            }
        )

        save_data(new_record, "tim.db", "Bodyweight")

    # Display current records
    bw = read_data("tim.db", "Bodyweight")
    st.dataframe(bw, use_container_width=True)

    # Delete functionality
    st.subheader("Delete a Weight Record")
    delete_date = st.selectbox("Select a Date to Delete", options=bw["Date"].unique())
    delete_button = st.button("Delete Record")

    if delete_button:
        # Call the delete function
        delete("tim.db", "Bodyweight", "Date", str(delete_date))
        st.success(f"Record for {delete_date} deleted successfully!")
        st.rerun()

    # Display graphs
    weight_graph, bmr_graph = st.columns(2)
    with weight_graph:
        fig = px.line(
            bodyweight_records, x="Date", y="Weight", title="Weight Over Time"
        )
        st.plotly_chart(fig)

    with bmr_graph:
        fig = px.line(bodyweight_records, x="Date", y="BMR", title="BMR Over Time")
        st.plotly_chart(fig)

    # st.header("Gym Exercises Tracker")
    # tab_leg, tab_back, tab_chest = st.tabs(["Leg Day", "Back Day", "Chest Day"])

    # days = ["Leg Day", "Back Day", "Chest Day"]
    # tabs = [tab_leg, tab_back, tab_chest]
    # for tab, day in zip(tabs, days):
    #     with tab:
    #         st.subheader(day)
    #         exercise_records = read_data("tim.db", day)
    #         exercise_tracker(exercise_records, day)

    default_food, custom_food = st.columns(2)
    with default_food:
        # Food Tracker
        st.header("Food Tracker")

        # User input text box
        user_input = st.text_input("Search for a food item:", "")

        # Filtering the dataframe based on the user input
        food_data = read_data("food_tim.db", "Foods")
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

            save_data(new_food, "food_tim.db", "Food Tracker")

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
                save_data(new_custom_food, "food_tim.db", "Foods")
                st.success(f"Custom food '{custom_food_name}' added successfully!")

    data = read_data("food_tim.db", "Food Tracker")
    st.dataframe(data.sort_values(by="Date"), use_container_width=True)

    st.header("Food Tracker Management")

    data = read_data("food_tim.db", "Food Tracker")
    if not data.empty:
        st.subheader("Delete a Food Item")
        # Create a multi-select box to choose the date and food item for deletion
        date_options = sorted(data['Date'].unique())
        selected_date_for_deletion = st.selectbox("Select Date", options=date_options, key="del_date")
        
        # Filter food items based on the selected date
        food_items = data[data['Date'] == selected_date_for_deletion]['Food Item'].unique()
        selected_food_item_for_deletion = st.selectbox("Select Food Item", options=food_items, key="del_food_item")
        
        delete_button = st.button("Delete Food Item")
        
        if delete_button:
            # Convert date to string as it's stored in the database
            selected_date_str = pd.to_datetime(selected_date_for_deletion).strftime('%Y-%m-%d')
            
            # Call the delete function to remove the selected food item
            delete("food_tim.db", "Food Tracker", "Date", selected_date_str, additional_condition=f"AND `Food Item` = '{selected_food_item_for_deletion}'")
            
            st.success(f"Food item '{selected_food_item_for_deletion}' on {selected_date_for_deletion} deleted successfully!")
            st.rerun()
    else:
        st.write("No food records to manage.")

    if data.empty:
        st.warning("No food records found.")
    else:
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



