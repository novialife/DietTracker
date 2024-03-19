import streamlit as st

def main():
    st.title("Welcome to Your Diet Tracker and Food Calculator!")

    st.header("What is this app?")
    st.write("""
    This app is designed to help you track your diet and calculate the nutritional value of your meals.
    Whether you're trying to maintain a balanced diet, lose weight, or simply keep track of your eating habits,
    our app provides the tools you need to stay on track.
    """)

    st.header("Features")
    st.write("""
    - **Food Calculator**: Calculate the nutritional content of your meals by selecting from a wide range of foods.
    - **Diet Tracking**: Keep a daily log of your food intake, gym workouts, and nutritional goals.
    """)

    st.header("How to Use")
    st.write("""
    Navigate through the app using the sidebar on the left. Select the feature you'd like to use, and you'll be guided through the process.
    It's that simple!
    """)

    st.header("Get Started")
    st.write("To begin, select a feature from the sidebar and start tracking your dietary habits today!")

if __name__ == "__main__":
    main()
