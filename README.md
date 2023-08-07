# fpl-predictor
Combining the Fantasy Premier League with a Neural Network pipeline

## Description
This repo is a research project to determine whether it is possible to use player data from publically availble APIs to accurately model performance of players in the Fantasy Premier League. This project will use the PyTorch deep learning framework as the basis of the ML model for predictions, with the long term aim of creating a public application where FPL players can use the tool to undertand the current and future performance of their team.

## Project Stages

### 1. Modelling Investigation
The first step is to at least confirm if a player's performance can be predicted using data, from here we will know whether this project is feasible. 

#### Findings - see notebooks/03_network_training.ipynb for details
1. After trying numerous hyperparameter combinations, it seems that the network quickly reaches a limit to how well it can learn the data, as the validation loss does not decrease after ~30 epochs of training. This, I believe, is due to the large variation in a given player's performance week by week.
2. Without making any plots, it did at least seem like the model was reasonably accurate at predicting when a player might score more than the average points, although exact preidctions were less common (e.g. predicted points==6, actual points==9 - both are high but the prediction is not technically correct). Because of this, any week by week model should only ever be used as a guide to estimate the highest scoring players in a gameweek, not necessarily as an accurate indicator of that player's exact points.
3. However, it certainly seemed like over a long period (e.g. a few months), the model could be accurate at understanding whether a player is 'unlucky' (model suggests a player should be getting more points than they are, so they are 'due' to start getting points soon) or simply just not performing (model predicts a low number of points). Over a long period, the randomness of each week is reduced and so the model could well be more accuate at detecting trends

#### Next Steps
1. Make some plots to visualise whether the model is accurate at predicting whether a player will get a 'high' score week by week. If so, the model can at least be used as a weekly guide to making transfers
2. Make some plots to visualise whether the model is accurate over longer periods of time where the randomness of each gameweek is better accounted for. If so, then the model can be used to understand if a player is 'unlucky', or just not performing well
3. Investigate new data sources 
