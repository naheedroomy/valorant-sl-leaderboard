import json

import streamlit as st
import requests

def display_account_info(account_json):
    st.subheader("Account Details")
    st.write(f"Name and Tag: {account_json['name_and_tag']}")
    st.write(f"Rank: {account_json['rank']}")
    st.write(f"Elo: {account_json['elo']}")


def show_registration_page():
    # heading
    st.markdown("""
        # Register your account
        """)

    # Initialize session state variables
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'code' not in st.session_state:
        st.session_state.code = ""
    if 'data' not in st.session_state:
        st.session_state.data = {}
    if '2fa_status' not in st.session_state:
        st.session_state['2fa_status'] = ""

    # Initialize session state variables
    if 'discord_id' not in st.session_state:
        st.session_state.discord_id = ""
    if 'discord_name' not in st.session_state:
        st.session_state.discord_name = ""
    if 'discord_discriminator' not in st.session_state:
        st.session_state.discord_discriminator = ""
    if 'discord_verified' not in st.session_state:
        st.session_state.discord_verified = False
    if 'show_confirm_buttons' not in st.session_state:
        st.session_state.show_confirm_buttons = False

    with st.form("discord_form"):
        st.markdown("""
            ### Why do we need your Discord ID?<br>
            We need your Discord ID to verify your identity, and to send you messages in case of a prize/giveaway.<br>
            We will **NOT** use your Discord ID for any other purpose, and it will be deleted after verifying.<br>           
            Your discord id is a 15-20 digit number that can be found by following the link below. (Example: 573602197214528560)<br>
            It is **NOT** your username. (**NOT** `username#1234`)
            """, unsafe_allow_html=True)
        st.markdown(
            """
            <a href="https://docs.google.com/document/d/e/2PACX-1vRxURta1FWaWBpOkKhMTEAVBW-D9_MmAHMwB9YsReJ7fFshWFKjNoD4vaM1_lHaOA_HIzCgxIvDVNaK/pub" target="_blank" style="display: inline-block; margin-bottom: 1rem;">How do I find my Discord ID?</a>
            """,
            unsafe_allow_html=True
        )
        if not st.session_state.discord_verified:
            st.session_state.discord_id = st.text_input("Discord ID", value=st.session_state.discord_id)
        submitted_discord = st.form_submit_button("Verify Discord ID")
        st.markdown("PS : If something goes wrong, just refresh the page. Still under development :)")
        if submitted_discord:
            with st.spinner("Verifying Discord ID..."):
                response = requests.post("http://localhost:8000/discord/verify_discord_id/",
                                         json={"discord_id": st.session_state.discord_id})
                if response.status_code == 200:
                    discord_data = response.json()
                    st.session_state.discord_name = discord_data["name"]
                    st.session_state.discord_discriminator = discord_data["discriminator"]

                    # Send a request to check if the Discord ID is already associated with a user
                    discord_username = f"{discord_data['name']}{discord_data['discriminator']}"
                    response = requests.get(f"http://localhost:8000/user/check-discord",
                                             json={"discord_username": discord_username
                                                    })
                    if response.status_code == 200:
                        st.markdown(f"""
                                    Discord Username succefully verified: **{discord_username}**<br>
                                    """, unsafe_allow_html=True)
                        st.session_state.discord_verified = True
                        st.session_state.show_confirm_buttons = True
                    else:
                        st.error(
                            "This Discord ID is already associated with a user. Please enter a different Discord ID.")
                else:
                    st.error("Invalid Discord ID. Please enter a valid Discord ID and try again.")

    if st.session_state.discord_verified:
        # Input fields for username and password
        with st.form("account_form"):
            st.subheader("Riot Account Details")
            st.session_state.username = st.text_input("Username", value=st.session_state.username)
            st.session_state.password = st.text_input("Password", value=st.session_state.password, type="password")

            submitted = st.form_submit_button("Submit")

        if submitted:
            with st.spinner("Checking account..."):
                response = requests.post("http://localhost:8000/account/login/riot",
                                         json={"username": st.session_state.username, "password": st.session_state.password})
                st.session_state.data = response.json()

                if st.session_state.data.get("status") == "error":
                    st.error(st.session_state.data.get("message"))

    # Display 2FA input field and button if status is "2FA" or if the latest 2FA status is "error"
    if st.session_state.data and st.session_state.data.get("status") == "2FA":
        with st.form("2fa_form"):
            st.session_state.code = st.text_input("2FA Code", value=st.session_state.code, max_chars=6,
                                                  key=st.session_state.code)
            submitted_2fa = st.form_submit_button("Submit 2FA Code")

        if submitted_2fa:
            with st.spinner("Verifying 2FA code..."):
                response = requests.post(
                    f"http://localhost:8000/account/login/riot/2fa/{st.session_state.username}?code={st.session_state.code}")
                new_data = response.json()
                if new_data.get("status") == "error":
                    st.error(new_data.get("message"))
                    st.session_state.code = ""
                    st.session_state['2fa_status'] = ""
                else:
                    st.session_state.data = new_data
                    st.session_state.code = ""

    if st.session_state.data.get("status") == "success":
        puuid = st.session_state.data["puuid"]

        # Check if the puuid already exists in the database
        check_puuid_response = requests.get(f"http://localhost:8000/user/check-puuid?puuid={puuid}")
        if check_puuid_response.status_code == 400:
            st.error("Riot account already exists. Please log in again.")
        else:
            account_details_response = requests.get(f"http://localhost:8000/account/get/puuid/{puuid}")
            account_json = account_details_response.json()
            display_account_info(account_json)

            discord_username = f"{st.session_state.discord_name}{st.session_state.discord_discriminator}"
            # Send a request to the /register/leaderboard API
            user_leaderboard_data = {
                "riot_username": account_json["name_and_tag"],
                "puuid": puuid,
                "discord_username": discord_username,
                "elo": account_json["elo"],
                "rank": account_json["rank"],
                "discord_id": st.session_state.discord_id
            }
            jsoned = json.dumps(user_leaderboard_data)
            print(jsoned)
            leaderboard_response = requests.post(
                "http://localhost:8000/leaderboard/register",
                json=user_leaderboard_data,
            )
            leaderboard_json = leaderboard_response.json()
            if leaderboard_response.status_code == 200:
                st.success(leaderboard_json.get("message"))
                st.markdown("[Join our Discord server!](https://discord.gg/kKVqZ4Du3J)")

            else:
                st.error(leaderboard_json.get("message"))