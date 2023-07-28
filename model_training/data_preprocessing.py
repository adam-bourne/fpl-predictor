import pandas as pd
import os
from sklearn.impute import SimpleImputer

latest_db_file = "whole_db_26_07_2023.csv"
# latest_db_file = "reduced_0_db_26_07_2023.csv"
data_fixtures_path = os.path.join(os.path.dirname(__file__), "data")

# FIXTURES
player_features_to_sum = [
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

team_features_to_sum = [
    "goals_conceded",
    "goals_scored",
    "player_team_points",
    "opponent_team_points",
]

####################################################################
# CONFIG
####################################################################


def player_team_points(was_home, h_score, a_score):
    """gets the points for a gw for the team a player plays for"""

    if was_home:
        if h_score == a_score:
            return 1
        if h_score > a_score:
            return 3
        else:
            return 0
    else:
        if h_score == a_score:
            return 1
        if h_score > a_score:
            return 0
        else:
            return 3


def opponent_points(player_team_points):
    """gets the points for a player's opposition team"""

    if player_team_points == 1:
        return 1
    if player_team_points == 3:
        return 0
    else:
        return 3


def impute_xg(df):
    """imputes xg values for previouse seasons as FPL only collected this data from 2223 onwards"""

    imputer = SimpleImputer(strategy="median")
    features_to_impute = [
        "expected_assists",
        "expected_goals",
        "expected_goals_conceded",
    ]

    for feature in features_to_impute:
        df[feature] = imputer.fit_transform(df[[feature]])

    return df


def player_sum(df, features_to_sum, sum_ranges):
    """takes the combined df and sums player attributes based on values provided in sum_range"""

    output_df = df.copy()
    summed_features = []

    for feature in features_to_sum:
        for _sum in sum_ranges:
            summed_feature = "last_" + str(_sum) + "_" + feature

            if _sum == "all":
                output_df[summed_feature] = (
                    output_df.sort_values("round")
                    .groupby(["season", "full_name"], group_keys=False)[feature]
                    .apply(lambda x: x.cumsum() - x)
                )

            else:
                output_df[summed_feature] = (
                    output_df.sort_values("round")
                    .groupby(["season", "full_name"], group_keys=False)[feature]
                    .apply(
                        lambda x: x.rolling(min_periods=1, window=_sum + 1).sum() - x
                    )
                )

            summed_features.append(summed_feature)

    return output_df, summed_features


def sum_team_2(df, sum_ranges):
    """takes the combined df and sums team attributes based on values provided in sum_range"""

    # reduce df size to make easier to handle
    output_df = df[
        [
            "player_team_name",
            "season",
            "round",
            "kickoff_time",
            "opponent_team_name",
            "goals_scored",
            "goals_conceded",
            "player_team_points",
        ]
    ].copy()

    # apply grouping to goals_scored and conceded to apply to whole team
    output_df["team_goals_scored"] = output_df.groupby(
        ["player_team_name", "season", "round", "kickoff_time", "opponent_team_name"]
    )["goals_scored"].transform("sum")
    output_df["team_goals_conceded"] = output_df.groupby(
        ["player_team_name", "season", "round", "kickoff_time", "opponent_team_name"]
    )["goals_conceded"].transform("max")
    output_df.drop(["goals_scored", "goals_conceded"], axis=1, inplace=True)

    # group whole dataframe
    player_team_grouped_df = (
        output_df.groupby(
            [
                "player_team_name",
                "season",
                "round",
                "kickoff_time",
                "opponent_team_name",
            ]
        )
        .mean()
        .reset_index()
    )

    summed_team_features = []
    for feature in ["team_goals_scored", "team_goals_conceded", "player_team_points"]:
        for _sum in sum_ranges:
            summed_player_team_feature_name = "last_player_" + str(_sum) + "_" + feature
            summed_opponent_team_feature_name = (
                "last_opponent_" + str(_sum) + "_" + feature
            )
            summed_team_features.extend(
                [summed_player_team_feature_name, summed_opponent_team_feature_name]
            )
            if _sum == "all":
                player_team_grouped_df[summed_player_team_feature_name] = (
                    player_team_grouped_df.sort_values("round")
                    .groupby(["player_team_name", "season"], group_keys=False)[feature]
                    .apply(lambda x: x.cumsum() - x)
                )
            else:
                player_team_grouped_df[
                    summed_player_team_feature_name
                ] = player_team_grouped_df.groupby(["player_team_name", "season"])[
                    feature
                ].transform(
                    lambda x: (x.rolling(min_periods=1, window=_sum + 1).sum() - x)
                )
            for index, row in player_team_grouped_df.iterrows():
                blub = player_team_grouped_df.loc[
                    (
                        player_team_grouped_df["player_team_name"]
                        == row["opponent_team_name"]
                    )
                    & (player_team_grouped_df["season"] == row["season"])
                    & (player_team_grouped_df["round"] == row["round"])
                    & (player_team_grouped_df["kickoff_time"] == row["kickoff_time"])
                    & (
                        player_team_grouped_df["opponent_team_name"]
                        == row["player_team_name"]
                    ),
                    summed_player_team_feature_name,
                ].item()
                player_team_grouped_df.loc[
                    index, summed_opponent_team_feature_name
                ] = blub

    # combine with the player df
    combined_df = df.merge(
        player_team_grouped_df,
        on=[
            "player_team_name",
            "season",
            "round",
            "kickoff_time",
            "opponent_team_name",
        ],
        how="left",
    )
    return combined_df, summed_team_features


def apply_preprocessing(db_file_path):
    """applies preprocessing steps to the dataframe"""

    raw_db = pd.read_csv(os.path.join(data_fixtures_path, db_file_path))
    raw_db_copy = raw_db.copy()

    # map funcs to our df
    raw_db_copy["player_team_points"] = raw_db_copy.apply(
        lambda x: player_team_points(x.was_home, x.team_h_score, x.team_a_score), axis=1
    )
    raw_db_copy["opponent_team_points"] = raw_db_copy.apply(
        lambda x: opponent_points(x.player_team_points), axis=1
    )

    # impute
    raw_db_copy = impute_xg(raw_db_copy)

    # create player summed table
    summed_gw_df_players, summed_player_features = player_sum(
        raw_db_copy, player_features_to_sum, ["all", 1, 3, 5]
    )

    # create team_sum table and combine
    combined_teams_players, summed_team_features = sum_team_2(
        summed_gw_df_players, ["all", 1, 3, 5]
    )

    return combined_teams_players, summed_player_features, summed_team_features


def save_dataframe(combined_df, player_features, team_features):
    """saves the preprocessed df to fiels"""

    features_for_modelling = (
        [
            "position",
            "was_home",
            "round",
            "minutes",
            "gw_total_points",
            "total_points_last_season",
        ]
        + player_features
        + team_features
    )
    combined_teams_players_lite = combined_df[features_for_modelling]
    combined_teams_players_lite.to_csv(
        os.path.join(data_fixtures_path, "combined_players_teams_lite.csv"), index=False
    )

    # We have a large number of rows with all 0s, due to sqaud players not being played
    # I can remove a lot of these so that we rebalance the dataset a biy more
    features_for_modelling_m = (
        [
            "position",
            "was_home",
            "round",
            "minutes",
            "gw_total_points",
            "total_points_last_season",
        ]
        + player_features
        + team_features
    )
    combined_teams_players_lite_w_min = combined_df[features_for_modelling_m]
    combined_teams_players_lite_w_min = combined_teams_players_lite_w_min.drop(
        combined_teams_players_lite_w_min[
            (combined_teams_players_lite_w_min["gw_total_points"] == 0)
            & (combined_teams_players_lite_w_min["minutes"] == 0)
        ]
        .sample(frac=0.95)
        .index
    )
    combined_teams_players_lite_w_min.drop(["minutes"], axis=1, inplace=True)
    combined_teams_players_lite_w_min.to_csv(
        os.path.join(data_fixtures_path, "combined_players_teams_lite_w_min.csv"),
        index=False,
    )


if __name__ == "__main__":
    combined_df, player_features, team_features = apply_preprocessing(latest_db_file)
    save_dataframe(combined_df, player_features, team_features)
