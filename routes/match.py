import requests
import math
from fastapi import APIRouter

from models.queue import MongoQueue

match = APIRouter(prefix="/match",  tags=["match"])

# @match.get("/matches/{name1}/{tag1}/{name2}/{tag2}")
# async def get_account_details(name1: str, tag1: str, name2: str, tag2: str):



























@match.get("/")
async def get_account_details():
    headers = {
        'accept': 'application/json',
    }
    match_history_response = requests.get(
        'https://api.henrikdev.xyz/valorant/v3/matches/ap/4dibb/rekt?filter=competitive',
        headers=headers)
    match_history_response_2 = requests.get(
        'https://api.henrikdev.xyz/valorant/v3/matches/ap/ace/dsl?filter=competitive',
        headers=headers)

    matches_data_p1 = match_history_response.json()["data"]
    matches_data_p2 = match_history_response_2.json()["data"]
    # get the value for the matchid field in each iteration of matches_data_p1

    # return matches_data_p1[0]["metadata"]["matchid"]

    #     write a for loop to return metadata for each matches_data_p1
    match_id_array_p1 = []
    match_id_array_p2 = []
    for match in matches_data_p1:
        metadata = {
            "match_id": match["metadata"]["matchid"],
        }
        match_id_array_p1.append(metadata)

    for match in matches_data_p2:
        metadata = {
            "match_id": match["metadata"]["matchid"],
        }
        match_id_array_p2.append(metadata)

    common_match_id = ""

    # compare the match_id_array_p1 and match_id_array_p2 and return the match_id of the match that is in both arrays
    for match in match_id_array_p1:
        for match2 in match_id_array_p2:
            if match["match_id"] == match2["match_id"]:
                common_match_id = match["match_id"]

    if common_match_id != "":

        match_details = requests.get('https://api.henrikdev.xyz/valorant/v2/match/' + common_match_id)

        team_win_red = match_details.json()["data"]["teams"]["red"]["has_won"]

        if team_win_red:
            team_win = "red"
            team_lose = "blue"
        else:
            team_win = "blue"
            team_lose = "red"

        rounds_won = str(match_details.json()["data"]["teams"][team_win]["rounds_won"])
        rounds_lost = str(match_details.json()["data"]["teams"][team_win]["rounds_lost"])

        final_score = rounds_won + "-" + rounds_lost

        total_round_number = int(rounds_lost) + int(rounds_won)

        # ECONOMY
        winning_p1_spent_per_thousand = match_details.json()["data"]["players"][team_win][0]["economy"]["spent"][
                                            "overall"] / 1000
        winning_p1_total_dmg = match_details.json()["data"]["players"][team_win][0]["damage_made"]
        winning_p1_econ_rating = math.ceil(winning_p1_total_dmg / winning_p1_spent_per_thousand)

        winning_p2_spent_per_thousand = match_details.json()["data"]["players"][team_win][1]["economy"]["spent"][
                                            "overall"] / 1000
        winning_p2_total_dmg = match_details.json()["data"]["players"][team_win][1]["damage_made"]
        winning_p2_econ_rating = math.ceil(winning_p2_total_dmg / winning_p2_spent_per_thousand)

        winning_p3_spent_per_thousand = match_details.json()["data"]["players"][team_win][2]["economy"]["spent"][
                                            "overall"] / 1000
        winning_p3_total_dmg = match_details.json()["data"]["players"][team_win][2]["damage_made"]
        winning_p3_econ_rating = math.ceil(winning_p3_total_dmg / winning_p3_spent_per_thousand)

        winning_p4_spent_per_thousand = match_details.json()["data"]["players"][team_win][3]["economy"]["spent"][
                                            "overall"] / 1000
        winning_p4_total_dmg = match_details.json()["data"]["players"][team_win][3]["damage_made"]
        winning_p4_econ_rating = math.ceil(winning_p4_total_dmg / winning_p4_spent_per_thousand)

        winning_p5_spent_per_thousand = match_details.json()["data"]["players"][team_win][4]["economy"]["spent"][
                                            "overall"] / 1000
        winning_p5_total_dmg = match_details.json()["data"]["players"][team_win][4]["damage_made"]
        winning_p5_econ_rating = math.ceil(winning_p5_total_dmg / winning_p5_spent_per_thousand)

        losing_p1_spent_per_thousand = match_details.json()["data"]["players"][team_lose][0]["economy"]["spent"][
                                           "overall"] / 1000
        losing_p1_total_dmg = match_details.json()["data"]["players"][team_lose][0]["damage_made"]
        losing_p1_econ_rating = math.ceil(losing_p1_total_dmg / losing_p1_spent_per_thousand)

        losing_p2_spent_per_thousand = match_details.json()["data"]["players"][team_lose][1]["economy"]["spent"][
                                           "overall"] / 1000
        losing_p2_total_dmg = match_details.json()["data"]["players"][team_lose][1]["damage_made"]
        losing_p2_econ_rating = math.ceil(losing_p2_total_dmg / losing_p2_spent_per_thousand)

        losing_p3_spent_per_thousand = match_details.json()["data"]["players"][team_lose][2]["economy"]["spent"][
                                           "overall"] / 1000
        losing_p3_total_dmg = match_details.json()["data"]["players"][team_lose][2]["damage_made"]
        losing_p3_econ_rating = math.ceil(losing_p3_total_dmg / losing_p3_spent_per_thousand)

        losing_p4_spent_per_thousand = match_details.json()["data"]["players"][team_lose][3]["economy"]["spent"][
                                           "overall"] / 1000
        losing_p4_total_dmg = match_details.json()["data"]["players"][team_lose][3]["damage_made"]
        losing_p4_econ_rating = math.ceil(losing_p4_total_dmg / losing_p4_spent_per_thousand)

        losing_p5_spent_per_thousand = match_details.json()["data"]["players"][team_lose][4]["economy"]["spent"][
                                           "overall"] / 1000
        losing_p5_total_dmg = match_details.json()["data"]["players"][team_lose][4]["damage_made"]
        losing_p5_econ_rating = math.ceil(losing_p5_total_dmg / losing_p5_spent_per_thousand)

        # KILLS
        winning_p1_kills = (match_details.json()["data"]["players"][team_win][0]["stats"]["kills"])
        winning_p2_kills = (match_details.json()["data"]["players"][team_win][1]["stats"]["kills"])
        winning_p3_kills = (match_details.json()["data"]["players"][team_win][2]["stats"]["kills"])
        winning_p4_kills = (match_details.json()["data"]["players"][team_win][3]["stats"]["kills"])
        winning_p5_kills = (match_details.json()["data"]["players"][team_win][4]["stats"]["kills"])

        losing_p1_kills = (match_details.json()["data"]["players"][team_lose][0]["stats"]["kills"])
        losing_p2_kills = (match_details.json()["data"]["players"][team_lose][1]["stats"]["kills"])
        losing_p3_kills = (match_details.json()["data"]["players"][team_lose][2]["stats"]["kills"])
        losing_p4_kills = (match_details.json()["data"]["players"][team_lose][3]["stats"]["kills"])
        losing_p5_kills = (match_details.json()["data"]["players"][team_lose][4]["stats"]["kills"])

        # DEATHS
        winning_p1_deaths = (match_details.json()["data"]["players"][team_win][0]["stats"]["deaths"])
        winning_p2_deaths = (match_details.json()["data"]["players"][team_win][1]["stats"]["deaths"])
        winning_p3_deaths = (match_details.json()["data"]["players"][team_win][2]["stats"]["deaths"])
        winning_p4_deaths = (match_details.json()["data"]["players"][team_win][3]["stats"]["deaths"])
        winning_p5_deaths = (match_details.json()["data"]["players"][team_win][4]["stats"]["deaths"])

        losing_p1_deaths = (match_details.json()["data"]["players"][team_lose][0]["stats"]["deaths"])
        losing_p2_deaths = (match_details.json()["data"]["players"][team_lose][1]["stats"]["deaths"])
        losing_p3_deaths = (match_details.json()["data"]["players"][team_lose][2]["stats"]["deaths"])
        losing_p4_deaths = (match_details.json()["data"]["players"][team_lose][3]["stats"]["deaths"])
        losing_p5_deaths = (match_details.json()["data"]["players"][team_lose][4]["stats"]["deaths"])

        # ASSISTS
        winning_p1_assists = (match_details.json()["data"]["players"][team_win][0]["stats"]["assists"])
        winning_p2_assists = (match_details.json()["data"]["players"][team_win][1]["stats"]["assists"])
        winning_p3_assists = (match_details.json()["data"]["players"][team_win][2]["stats"]["assists"])
        winning_p4_assists = (match_details.json()["data"]["players"][team_win][3]["stats"]["assists"])
        winning_p5_assists = (match_details.json()["data"]["players"][team_win][4]["stats"]["assists"])

        losing_p1_assists = (match_details.json()["data"]["players"][team_lose][0]["stats"]["assists"])
        losing_p2_assists = (match_details.json()["data"]["players"][team_lose][1]["stats"]["assists"])
        losing_p3_assists = (match_details.json()["data"]["players"][team_lose][2]["stats"]["assists"])
        losing_p4_assists = (match_details.json()["data"]["players"][team_lose][3]["stats"]["assists"])
        losing_p5_assists = (match_details.json()["data"]["players"][team_lose][4]["stats"]["assists"])

        # ACS
        winning_p1_acs = round(
            (match_details.json()["data"]["players"][team_win][0]["stats"]["score"]) / total_round_number)
        winning_p2_acs = round(
            (match_details.json()["data"]["players"][team_win][1]["stats"]["score"]) / total_round_number)
        winning_p3_acs = round(
            (match_details.json()["data"]["players"][team_win][2]["stats"]["score"]) / total_round_number)
        winning_p4_acs = round(
            (match_details.json()["data"]["players"][team_win][3]["stats"]["score"]) / total_round_number)
        winning_p5_acs = round(
            (match_details.json()["data"]["players"][team_win][4]["stats"]["score"]) / total_round_number)

        losing_p1_acs = round(
            (match_details.json()["data"]["players"][team_lose][0]["stats"]["score"]) / total_round_number)
        losing_p2_acs = round(
            (match_details.json()["data"]["players"][team_lose][1]["stats"]["score"]) / total_round_number)
        losing_p3_acs = round(
            (match_details.json()["data"]["players"][team_lose][2]["stats"]["score"]) / total_round_number)
        losing_p4_acs = round(
            (match_details.json()["data"]["players"][team_lose][3]["stats"]["score"]) / total_round_number)
        losing_p5_acs = round(
            (match_details.json()["data"]["players"][team_lose][4]["stats"]["score"]) / total_round_number)

        # KDA
        winning_p1_kda = round((winning_p1_kills + winning_p1_assists) / winning_p1_deaths, 2)
        winning_p2_kda = round((winning_p2_kills + winning_p2_assists) / winning_p2_deaths, 2)
        winning_p3_kda = round((winning_p3_kills + winning_p3_assists) / winning_p3_deaths, 2)
        winning_p4_kda = round((winning_p4_kills + winning_p4_assists) / winning_p4_deaths, 2)
        winning_p5_kda = round((winning_p5_kills + winning_p5_assists) / winning_p5_deaths, 2)

        losing_p1_kda = round((losing_p1_kills + losing_p1_assists) / losing_p1_deaths, 2)
        losing_p2_kda = round((losing_p2_kills + losing_p2_assists) / losing_p2_deaths, 2)
        losing_p3_kda = round((losing_p3_kills + losing_p3_assists) / losing_p3_deaths, 2)
        losing_p4_kda = round((losing_p4_kills + losing_p4_assists) / losing_p4_deaths, 2)
        losing_p5_kda = round((losing_p5_kills + losing_p5_assists) / losing_p5_deaths, 2)

        stats_winning_p1 = {
            "kills": str(winning_p1_kills),
            "deaths": str(winning_p1_deaths),
            "assists": str(winning_p1_assists),
            "total_score": str(match_details.json()["data"]["players"][team_win][0]["stats"]["score"]),
            "kda": str(winning_p1_kda),
            "acs": str(winning_p1_acs),
            "econ_rating": str(winning_p1_econ_rating)
        }
        stats_winning_p2 = {
            "kills": str(winning_p2_kills),
            "deaths": str(winning_p2_deaths),
            "assists": str(winning_p2_assists),
            "total_score": str(match_details.json()["data"]["players"][team_win][1]["stats"]["score"]),
            "kda": str(winning_p2_kda),
            "acs": str(winning_p2_acs),
            "econ_rating": str(winning_p2_econ_rating)
        }
        stats_winning_p3 = {
            "kills": str(winning_p3_kills),
            "deaths": str(winning_p3_deaths),
            "assists": str(winning_p3_assists),
            "total_score": str(match_details.json()["data"]["players"][team_win][2]["stats"]["score"]),
            "kda": str(winning_p3_kda),
            "acs": str(winning_p3_acs),
            "econ_rating": str(winning_p3_econ_rating)
        }
        stats_winning_p4 = {
            "kills": str(winning_p4_kills),
            "deaths": str(winning_p4_deaths),
            "assists": str(winning_p4_assists),
            "total_score": str(match_details.json()["data"]["players"][team_win][3]["stats"]["score"]),
            "kda": str(winning_p4_kda),
            "acs": str(winning_p4_acs),
            "econ_rating": str(winning_p4_econ_rating)
        }
        stats_winning_p5 = {
            "kills": str(winning_p5_kills),
            "deaths": str(winning_p5_deaths),
            "assists": str(winning_p5_assists),
            "total_score": str(match_details.json()["data"]["players"][team_win][4]["stats"]["score"]),
            "kda": str(winning_p5_kda),
            "acs": str(winning_p5_acs),
            "econ_rating": str(winning_p5_econ_rating)
        }

        stats_losing_p1 = {
            "kills": str(losing_p1_kills),
            "deaths": str(losing_p1_deaths),
            "assists": str(losing_p1_assists),
            "total_score": str(match_details.json()["data"]["players"][team_lose][0]["stats"]["score"]),
            "kda": str(losing_p1_kda),
            "acs": str(losing_p1_acs),
            "econ_rating": str(losing_p1_econ_rating)
        }
        stats_losing_p2 = {
            "kills": str(losing_p2_kills),
            "deaths": str(losing_p2_deaths),
            "assists": str(losing_p2_assists),
            "total_score": str(match_details.json()["data"]["players"][team_lose][1]["stats"]["score"]),
            "kda": str(losing_p2_kda),
            "acs": str(losing_p2_acs),
            "econ_rating": str(losing_p2_econ_rating)
        }
        stats_losing_p3 = {
            "kills": str(losing_p3_kills),
            "deaths": str(losing_p3_deaths),
            "assists": str(losing_p3_assists),
            "total_score": str(match_details.json()["data"]["players"][team_lose][2]["stats"]["score"]),
            "kda": str(losing_p3_kda),
            "acs": str(losing_p3_acs),
            "econ_rating": str(losing_p3_econ_rating)
        }
        stats_losing_p4 = {
            "kills": str(losing_p4_kills),
            "deaths": str(losing_p4_deaths),
            "assists": str(losing_p4_assists),
            "total_score": str(match_details.json()["data"]["players"][team_lose][3]["stats"]["score"]),
            "kda": str(losing_p4_kda),
            "acs": str(losing_p4_acs),
            "econ_rating": str(losing_p4_econ_rating)
        }
        stats_losing_p5 = {
            "kills": str(losing_p5_kills),
            "deaths": str(losing_p5_deaths),
            "assists": str(losing_p5_assists),
            "total_score": str(match_details.json()["data"]["players"][team_lose][4]["stats"]["score"]),
            "kda": str(losing_p5_kda),
            "acs": str(losing_p5_acs),
            "econ_rating": str(losing_p5_econ_rating)
        }

        winning_team_p1 = {
            "name": match_details.json()["data"]["players"][team_win][0]["name"],
            "tag": match_details.json()["data"]["players"][team_win][0]["tag"],
            "character": match_details.json()["data"]["players"][team_win][0]["character"],
            "stats": stats_winning_p1,
            # "stats": match_details.json()["data"]["players"][team_win][0]["stats"],
        }
        # create json objects for winning_team_p2, winning_team_p3, winning_team_p4, winning_team_p5
        winning_team_p2 = {
            "name": match_details.json()["data"]["players"][team_win][1]["name"],
            "tag": match_details.json()["data"]["players"][team_win][1]["tag"],
            "character": match_details.json()["data"]["players"][team_win][1]["character"],
            "stats": stats_winning_p2,

        }
        winning_team_p3 = {
            "name": match_details.json()["data"]["players"][team_win][2]["name"],
            "tag": match_details.json()["data"]["players"][team_win][2]["tag"],
            "character": match_details.json()["data"]["players"][team_win][2]["character"],
            "stats": stats_winning_p3,
        }
        winning_team_p4 = {
            "name": match_details.json()["data"]["players"][team_win][3]["name"],
            "tag": match_details.json()["data"]["players"][team_win][3]["tag"],
            "character": match_details.json()["data"]["players"][team_win][3]["character"],
            "stats": stats_winning_p4,
        }
        winning_team_p5 = {
            "name": match_details.json()["data"]["players"][team_win][4]["name"],
            "tag": match_details.json()["data"]["players"][team_win][4]["tag"],
            "character": match_details.json()["data"]["players"][team_win][4]["character"],
            "stats": stats_winning_p5,
        }

        # create json objects for losing_team_p1, losing_team_p2, losing_team_p3, losing_team_p4, losing_team_p5
        losing_team_p1 = {
            "name": match_details.json()["data"]["players"][team_lose][0]["name"],
            "tag": match_details.json()["data"]["players"][team_lose][0]["tag"],
            "character": match_details.json()["data"]["players"][team_lose][0]["character"],
            "stats": stats_losing_p1,
        }
        losing_team_p2 = {
            "name": match_details.json()["data"]["players"][team_lose][1]["name"],
            "tag": match_details.json()["data"]["players"][team_lose][1]["tag"],
            "character": match_details.json()["data"]["players"][team_lose][1]["character"],
            "stats": stats_losing_p2,
        }
        losing_team_p3 = {
            "name": match_details.json()["data"]["players"][team_lose][2]["name"],
            "tag": match_details.json()["data"]["players"][team_lose][2]["tag"],
            "character": match_details.json()["data"]["players"][team_lose][2]["character"],
            "stats": stats_losing_p3
        }
        losing_team_p4 = {
            "name": match_details.json()["data"]["players"][team_lose][3]["name"],
            "tag": match_details.json()["data"]["players"][team_lose][3]["tag"],
            "character": match_details.json()["data"]["players"][team_lose][3]["character"],
            "stats": stats_losing_p4
        }
        losing_team_p5 = {
            "name": match_details.json()["data"]["players"][team_lose][4]["name"],
            "tag": match_details.json()["data"]["players"][team_lose][4]["tag"],
            "character": match_details.json()["data"]["players"][team_lose][4]["character"],
            "stats": stats_losing_p5,
        }

        winning_team_details = {
            "p1": winning_team_p1,
            "p2": winning_team_p2,
            "p3": winning_team_p3,
            "p4": winning_team_p4,
            "p5": winning_team_p5,
        }

        losing_team_details = {
            "p1": losing_team_p1,
            "p2": losing_team_p2,
            "p3": losing_team_p3,
            "p4": losing_team_p4,
            "p5": losing_team_p5,
        }

        match_details_json = {
            "map": match_details.json()["data"]["metadata"]["map"],
            "match_id": match_details.json()["data"]["metadata"]["matchid"],
            "match_date": match_details.json()["data"]["metadata"]["game_start_patched"],
            "team_win": team_win,
            "final_score": final_score,
            "winning_team_players": winning_team_details,
            "losing_team_players": losing_team_details,
        }

        # return match_details.json()
        return match_details_json
    else:
        return "Error"