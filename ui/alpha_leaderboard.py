import streamlit as st
import pandas as pd
import requests

def show_alpha_leaderboard():
    st.title("Alpha Leaderboard")
    st.write("The Alpha (Platinum+) Queue Leaderboard. 10 mans are held in the discord server! :)")
    st.markdown("[Join the server!](https://discord.gg/kKVqZ4Du3J)")


    response = requests.get("http://localhost:8000/leaderboard/alpha")
    leaderboard_data = response.json()

    # Create a pandas DataFrame from the leaderboard data
    leaderboard_df = pd.DataFrame(leaderboard_data)

    # Reorganize the columns
    leaderboard_df = leaderboard_df[['name', 'win_loss', 'mmr']]
    leaderboard_df.columns = ['Name', 'Win-Loss', 'MMR']

    # Set the index to start at 1
    leaderboard_df.index = leaderboard_df.index + 1

    # Display the leaderboard data as a simple table
    st.table(leaderboard_df)