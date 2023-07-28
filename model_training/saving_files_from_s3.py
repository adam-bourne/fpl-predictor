import os
import boto3

# FIXTURES
local_data_path = "data"
bucket_name = "fpl-predictor"
s3 = boto3.client("s3")

####################################################################
# CONFIG
####################################################################


def save_elements_tables(season):
    """saves a local copy of the elements table for a specific season"""

    s3_elements_path = os.path.join(season, "players_raw.csv")
    local_elements_path = os.path.join(local_data_path, season)

    try:
        # make the directory if we don't already have it
        if not os.path.exists(local_elements_path):
            os.makedirs(local_elements_path)
        s3.download_file(
            bucket_name,
            s3_elements_path,
            os.path.join(local_elements_path, "elements_table.csv"),
        )
        print(f"{s3_elements_path} saved to {local_elements_path}!")

    except Exception as e:
        print(f"Unable to save elements_table because of: {e}")


def save_fixtures_tables(season):
    """saves a local copy of the fixtures table for a specific season"""

    s3_fixtures_path = os.path.join(season, "fixtures.csv")
    local_fixtures_path = os.path.join(local_data_path, season)

    try:
        # make the directory if we don't already have it
        if not os.path.exists(local_fixtures_path):
            os.makedirs(local_fixtures_path)
        s3.download_file(
            bucket_name,
            s3_fixtures_path,
            os.path.join(local_fixtures_path, "fixtures.csv"),
        )
        print(f"{s3_fixtures_path} saved to {local_fixtures_path}!")

    except Exception as e:
        print(f"Unable to save fixtures table because of: {e}")


def save_teams_tables(season):
    """saves a local copy of the teams table for a specific season"""

    s3_teams_path = os.path.join(season, "teams.csv")
    local_teams_path = os.path.join(local_data_path, season)

    try:
        # make the directory if we don't already have it
        if not os.path.exists(local_teams_path):
            os.makedirs(local_teams_path)
        s3.download_file(
            bucket_name, s3_teams_path, os.path.join(local_teams_path, "teams.csv")
        )
        print(f"{s3_teams_path} saved to {local_teams_path}!")

    except Exception as e:
        print(f"Unable to save teams table because of: {e}")


def save_merged_gw_tables(season):
    """saves a local copy of the teams table for a specific season"""

    s3_merged_gw_path = os.path.join(season, "merged_gw.csv")
    local_merged_gw_path = os.path.join(local_data_path, season)

    try:
        # make the directory if we don't already have it
        if not os.path.exists(local_merged_gw_path):
            os.makedirs(local_merged_gw_path)
        s3.download_file(
            bucket_name,
            s3_merged_gw_path,
            os.path.join(local_merged_gw_path, "merg.csv"),
        )
        print(f"{s3_merged_gw_path} saved to {local_merged_gw_path}!")

    except Exception as e:
        print(f"Unable to save merged_gw_table table because of: {e}")


def save_player_data(season):
    """saves the player gameweek table for each player in teh fpl for a given season"""

    s3_player_path = f"{season}/players/"
    local_players_path = os.path.join(local_data_path, season, "players")

    for player_directory in s3.list_objects(Bucket=bucket_name, Prefix=s3_player_path)[
        "Contents"
    ]:
        key = player_directory["Key"]
        if key.endswith("gw.csv"):
            player_name = os.path.basename(os.path.dirname(key)).lower()
            local_gw_path = os.path.join(local_players_path, player_name)

            # make the directory if we don't already have it
            if not os.path.exists(local_gw_path):
                os.makedirs(local_gw_path)

            s3.download_file(bucket_name, key, os.path.join(local_gw_path, "gw.csv"))
            print(f"{key} saved to {os.path.join(local_gw_path, 'gw.csv')}!")
        else:
            pass


if __name__ == "__main__":
    # save elements and player tables
    season_list = [
        "2016-17",
        "2017-18",
        "2018-19",
        "2019-20",
        "2020-21",
        "2021-22",
        "2022-23",
    ]

    for season in season_list:
        save_elements_tables(season)
        save_fixtures_tables(season)
        save_player_data(season)
        print("elements tables and player tables updated for every season")
