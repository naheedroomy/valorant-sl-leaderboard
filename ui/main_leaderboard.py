import streamlit as st
import pandas as pd
import requests

def show_main_leaderboard():
# Fetch the leaderboard data
    st.title("Sri Lanka Valorant Leaderboard")
    st.write("To register yourself on the leaderboard, click on the 'Register' button on the sidebar.")
    st.write("Ranks are updated every 15 minutes.")
    # make the above text a link to the register page
    st.markdown("[Join our Discord server!](https://discord.gg/sPVwAFNuV)")

    response = requests.get("http://localhost:8000/leaderboard/show/all")
    leaderboard_data = response.json()

    # Create a pandas DataFrame from the leaderboard data
    leaderboard_df = pd.DataFrame(leaderboard_data)

    # Split the riot_username into Username and Tag
    leaderboard_df['Username'], leaderboard_df['Tag'] = zip(*leaderboard_df['riot_username'].apply(
        lambda x: x.split('#')))

    # Strip any preceding or trailing spaces from the Username
    leaderboard_df['Username'] = leaderboard_df['Username'].str.strip()

    # Replace spaces with %20 in the Username
    leaderboard_df['Username'] = leaderboard_df['Username'].str.replace(" ", "%20")

    # Reorganize the columns
    leaderboard_df = leaderboard_df[['Username', 'Tag', 'elo', 'rank']]
    leaderboard_df.columns = ['Username', 'Tag', 'Elo', 'Rank']

    # Round the Elo values to integers
    leaderboard_df['Elo'] = leaderboard_df['Elo'].astype(int)
    # Set the index to start at 1
    leaderboard_df.index = leaderboard_df.index + 1

    # Create an HTML table with extended column widths, clickable usernames, hover effect on rows, and tooltips for tags
    table_html = """
        <style>
            table {
                width: 100%;
            }
            th, td {
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #525252;
            }
            th:nth-child(2), td:nth-child(2) {
                width: 40%;
            }
            th:nth-child(3), td:nth-child(3) {
                width: 30%;
            }
            th:nth-child(4), td:nth-child(4) {
                width: 30%;
            }
            tr:hover {
                background-color: #525252;
            }
        </style>
        <table>
            <tr><th></th><th>Username</th><th>Elo</th><th>Rank</th></tr>
        """

    for index, row in leaderboard_df.iterrows():
        username = row['Username'].replace('%20', ' ')
        table_html += f"<tr><td>{index}</td><td><a href='https://tracker.gg/valorant/profile/riot/{row['Username']}%23{row['Tag']}/overview' target='_blank' title='{username}#{row['Tag']}' style='text-decoration: underline; color: inherit;'>{username}</a></td><td>{row['Elo']}</td><td>{row['Rank']}</td></tr>"

    # Display the leaderboard data as a table with extended column widths, clickable usernames, hover effect on rows, and tooltips for tags
    st.markdown(table_html, unsafe_allow_html=True)