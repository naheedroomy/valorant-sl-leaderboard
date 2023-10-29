import pandas as pd
import requests

import streamlit as st

from main_leaderboard import show_main_leaderboard
from registration_page import show_registration_page
from alpha_leaderboard import show_alpha_leaderboard
from placeholder import show_placeholder_alpha, show_placeholder_omega
from omega_leaderboard import show_omega_leaderboard

st.set_page_config(page_title="SL Valorant Leaderboard",
                   page_icon="https://www.kindpng.com/picc/m/130-1306616_lk-sri-lanka-flag-icon-sri-lanka-flag.png")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


def get_rank_color(rank):
    if "Iron" in rank:
        return "black"
    elif "Bronze" in rank:
        return "peru"
    elif "Silver" in rank:
        return "silver"
    elif "Gold" in rank:
        return "gold"
    elif "Platinum" in rank:
        return "deepskyblue"
    elif "Diamond" in rank:
        return "purple"
    elif "Ascendant" in rank:
        return "green"
    elif "Immortal" in rank:
        return "red"
    elif "Radiant" in rank:
        return "goldenrod"
    else:
        return "black"


page = st.sidebar.radio("Navigation: ", ("Competitive Ranked Leaderboard", "10 mans - Alpha Leaderboard", "10 mans - Omega Leaderboard", "Register"))

if page == "Register":
    show_registration_page()

elif page == "Competitive Ranked Leaderboard":
    show_main_leaderboard()

elif page == "10 mans - Alpha Leaderboard":
    st.title("Alpha Leaderboard")
    st.write("The Alpha (Platinum+) Queue Leaderboard. 10 mans are held in the discord server! :)")
    st.markdown("[Join the server!](https://discord.gg/kKVqZ4Du3J)")
    success = show_alpha_leaderboard()


elif page == "10 mans - Omega Leaderboard":
    st.title("Omega Leaderboard")
    st.write("The Omega (Iron-Gold) Queue Leaderboard. 10 mans are held in the discord server! :)")
    st.markdown("[Join the server!](https://discord.gg/kKVqZ4Du3J)")
    success = show_omega_leaderboard()
    # if not success:
    #     show_placeholder_omega()
