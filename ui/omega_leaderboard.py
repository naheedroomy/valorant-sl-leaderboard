import streamlit as st
import pandas as pd
import requests


def show_omega_leaderboard():
    response = requests.get("http://localhost:8000/leaderboard/omega")
    leaderboard_data = response.json()

    if leaderboard_data == []:
        return False

    # Create a pandas DataFrame from the leaderboard data
    leaderboard_df = pd.DataFrame(leaderboard_data)

    # Reorganize the columns
    leaderboard_df = leaderboard_df[['name', 'win_loss', 'mmr']]
    leaderboard_df.columns = ['Name', 'Win-Loss', 'MMR']

    # Set the index to start at 1
    leaderboard_df.index = leaderboard_df.index + 1

    # Display the leaderboard data as a simple table
    st.table(leaderboard_df)