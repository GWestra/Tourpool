# Tourpool

### Goal

The goal of the project is to select the best team possible for the Tour de France. This team selection is based on results of riders earlier in the year. Using a Linear Programming approach the best possible team selection is made based on input parameters of the user. The data is either provided by the Tourpoolcommission (rider selection sheet) or webscraped from ProCyclingStats.com (rider results).

### About

The use can define a couple parameters in order to influence the team selection, that is:

|Parameter|Description|Example|
|---|---|---|
|`points`|Scoring system that is used for optimisation, either from UCI or ProCyclingStats.|`PCS`|
|`metric`|Metric that is used for optimisation.|`sum`|
|`n_selection`|Number of riders selected for the team.|`15`|
|`budget`|Available budget for the team.|`100`|
|`month_multipliers`|Multiplier for points earned in specific months. This is a list containing all 12 months in a year with the corresponding multiplier.|`{'January': 1,'February': 1,'March': 1,'April': 1,'May': 2,'June': 2,'July': 0,'August': 0,'September': 0,'October': 0,'November': 0,'December': 0,}`|
