#!/bin/bash

# Run invite.py in the background and redirect stdout/stderr to nohup.out
nohup python utils/bot1.py > nohup_discord_bot.out 2>&1 &
nohup python utils/bot2.py > nohup_discord_bot.out 2>&1 &


# Run update_db.py in the background and redirect stdout/stderr to nohup.out
nohup python utils/update_db.py >> nohup_update_db.out 2>&1 &

# Run uvicorn in the background and redirect stdout/stderr to nohup.out
nohup uvicorn app:app --reload --host 0.0.0.0 --port 8000 >> nohup_uvicorn.out 2>&1 &

# Run streamlit in the background and redirect stdout/stderr to nohup.out
nohup streamlit run ui/frontend.py --server.port 8501 >> nohup_streamlit.out 2>&1 &
