# fpl-predictor
Using data science to dig deeper into the Fantasy Premier League

## Description
This repo is a research project to understand how various DS/ML approaches can be used to understand, track, and predict the performance of football players in the FPL. All dta used will be from publicly available APIs. 

## Project Stages

### 1. Predicting player performance week by week - SHELVED
This stage will use the PyTorch deep learning framework as the basis of the ML model for predictions, with the long term aim of creating a public application where FPL players can use the tool to undertand the current and future performance of their team.

#### Modelling Investigation
The first step is to at least confirm if a player's performance can be predicted using data, from here we will know whether this project is feasible. 

#### Findings - see notebooks/03_network_training.ipynb for details
1. After trying numerous hyperparameter combinations, it seems that the network quickly reaches a limit to how well it can learn the data, as the validation loss does not decrease after ~30 epochs of training. This, I believe, is due to the large variation in a given player's performance week by week.
2. Without making any plots, it did at least seem like the model was reasonably accurate at predicting when a player might score more than the average points, although exact preidctions were less common (e.g. predicted points==6, actual points==9 - both are high but the prediction is not technically correct). Because of this, any week by week model should only ever be used as a guide to estimate the highest scoring players in a gameweek, not necessarily as an accurate indicator of that player's exact points.
3. However, it certainly seemed like over a long period (e.g. a few months), the model could be accurate at understanding whether a player is 'unlucky' (model suggests a player should be getting more points than they are, so they are 'due' to start getting points soon) or simply just not performing (model predicts a low number of points).
4. From these findings, it seems like there is simply too much outside factors not captured in our data to make accurate predictions week by week. Factors such as player fatigue, opposition tactics, morale etc cannot be captured in the data we have, and therefore too much random variation occurs to make weekly predictions - for now, this project idea is paused.

### 2. Analysing long term trends
This stage will aim to use data science to track the long term trends in a player's performance, and try to understand if they are overperforming (scoring more points than their underlying statistics suggest) or underperforming (scoring less points than their underlying statistics suggest). Having this data helps managers understand whether to transfer a player in/out

#### Modelling Investigation - ONGOING
For this section, I have decided to build separate models for each player position (GKP, DEF, MID and FWD) because each rely on pretty different underlying data to predict their FPL points. The basic idea will be to create a model which predicts a player's points across multiple games or a whole season. For example, rather than predict a player's points in an individual week, this model will take in a player's underlying stats for the whole season up to that point, and try to understand how many points that player should be on. 
