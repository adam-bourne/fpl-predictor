import pandas as pd
import os
from datetime import date

today = date.today().strftime("%d_%m_%Y")
data_fixtures_path = os.path.join(os.path.dirname(__file__), "data")

# FIXTURES
element_dict = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
key_features = [
    "full_name",
    "element",
    "season",
    "position_y",
    "player_team_name_from_fixtures",
    "round",
    "kickoff_time",
    "opponent_team_name",
    "was_home",
    "team_h_score",
    "team_a_score",
    "total_points",
    "total_points_last_season",
    "expected_assists",
    "expected_goals",
    "expected_goals_conceded",
    "assists",
    "bonus",
    "bps",
    "creativity",
    "clean_sheets",
    "goals_conceded",
    "goals_scored",
    "ict_index",
    "influence",
    "minutes",
    "threat",
    "expected_assists",
    "expected_goals",
    "expected_goals_conceded",
]

####################################################################
# CONFIG
####################################################################


def get_data_files():
    """creates dfs of all the raw data files"""

    # get our elements tables
    elements_1819 = pd.read_csv("data/2018-19/elements_table.csv")
    elements_1920 = pd.read_csv("data/2019-20/elements_table.csv")
    elements_2021 = pd.read_csv("data/2020-21/elements_table.csv")
    elements_2122 = pd.read_csv("data/2021-22/elements_table.csv")
    elements_2223 = pd.read_csv("data/2022-23/elements_table.csv")

    # get our gw tables
    gw_1819 = pd.read_csv("data/2018-19/merged_gw.csv", encoding="latin")
    gw_1920 = pd.read_csv("data/2019-20/merged_gw.csv", encoding="latin")
    gw_2021 = pd.read_csv("data/2020-21/merged_gw.csv", encoding="latin")
    gw_2122 = pd.read_csv("data/2021-22/merged_gw.csv", encoding="latin")
    gw_2223 = pd.read_csv("data/2022-23/merged_gw.csv", encoding="latin")

    # get our fixtures tables
    fixtures_1819 = pd.read_csv("data/2018-19/fixtures.csv")
    fixtures_1920 = pd.read_csv("data/2019-20/fixtures.csv")
    fixtures_2021 = pd.read_csv("data/2020-21/fixtures.csv")
    fixtures_2122 = pd.read_csv("data/2021-22/fixtures.csv")
    fixtures_2223 = pd.read_csv("data/2022-23/fixtures.csv")

    # master teams table
    master_teams = pd.read_csv("data/master_team_list.csv")

    elements_df_list = [
        elements_1819,
        elements_1920,
        elements_2021,
        elements_2122,
        elements_2223,
    ]
    gw_dfs_list = [gw_1819, gw_1920, gw_2021, gw_2122, gw_2223]
    fixtures_list = [
        fixtures_1819,
        fixtures_1920,
        fixtures_2021,
        fixtures_2122,
        fixtures_2223,
    ]

    return elements_df_list, gw_dfs_list, fixtures_list, master_teams


def prepare_dataframes(elements_df_list, gw_dfs_list, fixtures_list):
    """adds the season column as an identifier to each dataframe, and esures names are in the same format"""
    # add season to our dfs
    seasons = ["1819", "1920", "2021", "2122", "2223"]

    for i, season in enumerate(seasons):
        elements_df_list[i]["season"] = season
        gw_dfs_list[i]["season"] = season
        fixtures_list[i]["season"] = season
        for row_index, row in gw_dfs_list[i].iterrows():
            # make sure we have the same name format in the elements and gw tables
            first_name = (
                elements_df_list[i]
                .loc[elements_df_list[i]["id"] == row["element"], "first_name"]
                .item()
            )
            last_name = (
                elements_df_list[i]
                .loc[elements_df_list[i]["id"] == row["element"], "second_name"]
                .item()
            )
            gw_dfs_list[i].loc[row_index, "first_name"] = first_name
            gw_dfs_list[i].loc[row_index, "last_name"] = last_name

    # combine dataframes from all seasons into one
    total_elements_df = pd.concat(elements_df_list, ignore_index=True)
    total_gws_df = pd.concat(gw_dfs_list, ignore_index=True)
    total_fixtures_df = pd.concat(fixtures_list, ignore_index=True)

    return total_elements_df, total_gws_df, total_fixtures_df


def clean_names(total_elements_df, total_gws_df):
    """takes each combined df and performs cleaning of the names which need to be consistent throughout"""

    total_elements_df["full_name"] = (
        total_elements_df["first_name"] + "_" + total_elements_df["second_name"]
    )
    total_elements_df["full_name"] = total_elements_df["full_name"].str.lower()
    total_elements_df["position"] = total_elements_df.element_type.map(element_dict)
    total_gws_df["full_name"] = (
        total_gws_df["first_name"] + "_" + total_gws_df["last_name"]
    )
    total_gws_df["full_name"] = total_gws_df["full_name"].str.lower()

    return total_elements_df, total_gws_df


def merge_and_reduce(total_elements_df, total_gws_df, total_fixtures_df, master_teams):
    """merges all dataframes into a single dataframe, and extracts each player's team from the fixture table.
    This is necessary because the elements table doesn't account for players who moved team mid-season
    """

    # merge with gws_df and add opponenent team name
    total_elements_df_lite = total_elements_df[
        ["full_name", "season", "position", "total_points"]
    ]
    total_elements_df_lite.rename(
        columns={"total_points": "total_points_last_season"}, inplace=True
    )
    total_gws_df = total_gws_df.merge(
        total_elements_df_lite, on=["full_name", "season"], how="left"
    )
    for i, row in total_gws_df.iterrows():
        # unpack row vars
        fixture = row["fixture"]
        home_or_away = "team_h" if row["was_home"] else "team_a"

        # get player team code from fixtures
        player_team_code = total_fixtures_df.loc[
            (total_fixtures_df["season"] == row["season"])
            & (total_fixtures_df["id"] == fixture),
            home_or_away,
        ].item()

        # unpack from master team list
        player_team_name_from_fixtures = master_teams.loc[
            (master_teams["season"] == int(row["season"]))
            & (master_teams["team"] == player_team_code),
            "team_name",
        ].item()

        # unpack opponent team from master list
        opponent_team_name = master_teams.loc[
            (master_teams["season"] == int(row["season"]))
            & (master_teams["team"] == int(row["opponent_team"])),
            "team_name",
        ].item()

        # assign to main df
        total_gws_df.loc[
            i, "player_team_name_from_fixtures"
        ] = player_team_name_from_fixtures
        total_gws_df.loc[i, "opponent_team_name"] = opponent_team_name

    # reduce the dataframe to only the key attributes for modelling
    total_gws_df_lite = total_gws_df[key_features]
    total_gws_df_lite = total_gws_df_lite.loc[
        :, ~total_gws_df_lite.columns.duplicated()
    ].copy()
    total_gws_df_lite.rename(
        columns={
            "position_y": "position",
            "total_points": "gw_total_points",
            "player_team_name_from_fixtures": "player_team_name",
        },
        inplace=True,
    )

    total_gws_df_lite["total_points_last_season"] = total_gws_df_lite[
        "total_points_last_season"
    ].fillna(0)
    total_gws_df_lite.dropna(subset=["position", "team_a_score"], inplace=True)

    # save to drive
    total_gws_df_lite.to_csv(f"data/db_tables/whole_db_{today}.csv", index=False)


if __name__ == "__main__":
    elements_list, gw_list, fixtures_list, teams = get_data_files()
    total_elements, total_gws, total_fixtures = prepare_dataframes(
        elements_list, gw_list, fixtures_list
    )
    total_elements, total_gws = clean_names(total_elements, total_gws)
    merge_and_reduce(total_elements, total_gws, total_fixtures, teams)
