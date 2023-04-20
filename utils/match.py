from typing import List, Optional

from models.queue import MongoQueue
from models.user import MongoUser, MongoMatch


def create_match():
    processing_queue = MongoQueue.objects().first()

    #  get the first 10 players in the queue
    players_in_queue = processing_queue.players_in_queue
    players_in_queue = players_in_queue[:10]

    #  for each of the players_in_queue, get their relevant object from MongoUser colleciton
    players_in_queue_objects = []
    for player in players_in_queue:
        player_object = MongoUser.objects.get(id=player)
        players_in_queue_objects.append(player_object)
    #  sort the players_in_queue_objects by elo
    players_in_queue_objects.sort(key=lambda x: x.elo, reverse=True)

    #  create a list of the player ids
    players_in_queue_ids = []
    for player in players_in_queue_objects:
        players_in_queue_ids.append(player.puuid)

    team1_list = [players_in_queue_ids[0], players_in_queue_ids[2], players_in_queue_ids[4], players_in_queue_ids[7],
                  players_in_queue_ids[9]]
    team2_list = [players_in_queue_ids[1], players_in_queue_ids[3], players_in_queue_ids[5], players_in_queue_ids[6],
                  players_in_queue_ids[8]]

    team_1_captain = team1_list[0]
    team_2_captain = team2_list[0]

    players = players_in_queue_ids

    #  create a new match object
    new_match = MongoMatch(
        players=players,
        team_1=team1_list,
        team_2=team2_list,
        team_1_cap=team_1_captain,
        team_2_cap=team_2_captain
    )
    new_match.save()

# change the queue to inactive
    processing_queue.is_active = False
    processing_queue.status = "Queue completed"
    processing_queue.save()


