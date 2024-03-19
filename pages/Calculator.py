import streamlit as st
import pandas as pd
import sqlite3
from db import read_data


# Function to connect to the database and fetch data
def load_data():
    conn = sqlite3.connect('food.db')
    query = "SELECT * FROM Foods"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to calculate total nutrients based on selected foods and their quantities
def calculate_totals(selected_foods, quantities):
    total_carbs = sum(selected_foods["Carbohydrate, by difference"] * quantities / 100)
    total_energy = sum(selected_foods["Energy (kcal)"] * quantities / 100)
    total_protein = sum(selected_foods["Protein"] * quantities / 100)
    total_fat = sum(selected_foods["Total lipid (fat)"] * quantities / 100)
    return total_carbs, total_energy, total_protein, total_fat

def main():
    # Load data from the database
    df = read_data("food.db", "Foods")

    # Streamlit UI
    st.title("Nutrient Calculator")

    # Multiselect box to select foods
    selected_food_descriptions = st.multiselect("Select Foods", df["description"].unique())

    # Empty dictionary to hold quantities for each selected food
    quantities = {}

    # For each selected food, create a number input for quantity
    for food in selected_food_descriptions:
        quantities[food] = st.number_input(f"Quantity for {food} (in servings)", min_value=0.0, value=1.0, step=0.5)

    # Filter dataframe based on selected foods
    filtered_df = df[df["description"].isin(selected_food_descriptions)]

    # Adjust the filtered_df to include quantities
    if filtered_df.empty:
        st.write("Please select at least one food item.")
    else:
        filtered_df["Quantity"] = filtered_df["description"].map(quantities)

    # Button to calculate and display total nutrients
    if st.button("Calculate"):
        if filtered_df.empty:
            st.write("Please select at least one food item and set quantities.")
        else:
            # Use the "Quantity" column for calculations
            total_carbs, total_energy, total_protein, total_fat = calculate_totals(filtered_df, filtered_df["Quantity"])
            st.write(f"Total Carbohydrate, by difference: {total_carbs:.2f} g")
            st.write(f"Total Energy: {total_energy:.2f} kcal")
            st.write(f"Total Protein: {total_protein:.2f} g")
            st.write(f"Total Lipid (fat): {total_fat:.2f} g")


if __name__ == "__main__":
    main()