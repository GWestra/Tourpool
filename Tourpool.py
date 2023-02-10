import pandas as pd
from datetime import datetime
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable


# Define functions
def read_data():
    """Read processed data for AFM Tourpool 2022 from Github repo."""
    
    file_path = 'https://raw.githubusercontent.com/GWestra/Tourpool/main/Data/'
    file_name_tourpool = 'Tourpool.csv'
    file_name_results = 'PCS_results.csv'
    
    df_tourpool = pd.read_csv('/'.join([file_path,file_name_tourpool]), sep=';', encoding='utf8')
    df_results = pd.read_csv('/'.join([file_path,file_name_results]), sep=';', encoding='utf8')
    
    # Data preparation
    df_results['PointsPCS'] = df_results['PointsPCS'].replace('-','0').astype(float)
    df_results['PointsUCI'] = df_results['PointsUCI'].replace('-','0').astype(float)
        
    # Some riders dropped out before the start of the Tour de France
    # Change value of these riders to 999, such that they will not be selected in the model
    df_tourpool.loc[df_tourpool['TP_Status'] == "niet gestart",'Waarde'] = 999
    
    return df_tourpool, df_results


def get_month_multiplier(date, month_multipliers):  
    return month_multipliers[datetime.strptime(date, '%d-%m-%Y').strftime('%B')]


def aggregate_results(df, points, metric, month_multipliers):
    """Calculate total points per rider for chosen metric and source."""
    
    if points not in ['PCS','UCI']:
        raise ValueError('WARNING! Invalid input for {points}. Choose from: [PCS, UCI].')
    
    if metric not in ['count','mean','sum']:
        raise ValueError('WARNING! Invalid input for {metric}. Choose from: [count, mean, sum].')
    
    # Find column to aggregate
    col = ''.join(['Points', points])
    
    # Multiply points with month multiplier
    df['AggPoints'] = df[col] * df['Date'].map(lambda date: get_month_multiplier(date, month_multipliers))
    
    # Aggregate for each rider
    return df.groupby('NamePCS').aggregate({'AggPoints': metric})


def run_linear_program(df, n_selection, budget):
    """Specify and try to solve linear program of the Tourpool."""
    
    try:
        int(n_selection)
    except:
        raise ValueError('WARNING! Invalid input for {n_selection}. Choose an integer!')
    
    try:
        n_selection > 0
    except:
        raise ValueError('WARNING! Invalid input for {n_selection}. Choose a positive integer!')
        
    try:
        float(budget)
    except:
        raise ValueError('WARNING! Invalid input for {budget}. Budget should be numerical!')
    
    
    # Specify Linear problem 
    model = LpProblem(name="TourpoolSelection", sense=LpMaximize)
    
    # Define decision variables
    x = {i: LpVariable(name=f'x{i}', cat='Binary') for i in range(0,len(df))}
    
    # Add constraints
    model += (lpSum(x.values()) == n_selection, "Selection")
    model += (sum([x[i]*df.loc[i,'Waarde'] for i in range(0,len(df))]) <= budget, "Budget")
    
    # Set objective
    model += sum([x[i]*df.loc[i,'AggPoints'] for i in range(0,len(df))])
    
    # Solve optimisation problem
    model.solve()
    
    # Get the results
    selection = df.loc[[int(x.name.replace('x','')) for x in x.values() if x.value() == 1],'Renner']
    points_selected_team = df.loc[selection.index,'TP_PntTotaal'].sum()
    
    print(f"status: {model.status}, {LpStatus[model.status]}")
    print(f"objective: {model.objective.value()}")
    print(f"Number of riders selected: {len(selection)}")
    print(f"Budget left: {budget - df.loc[[int(x.name.replace('x','')) for x in x.values() if x.value() == 1],'Waarde'].sum()}")
    print(f"\nFinal result calculated! This team would have scored {points_selected_team} points")
    
    return selection


def run_tourpool(df_tourpool, df_results, points, metric, n_selection, budget, month_multipliers):
    
    # Aggregate data
    df = aggregate_results(df_results, points, metric, month_multipliers)
    df = df_tourpool.merge(df, on='NamePCS', how='left')
    
    # Run Linear program    
    return run_linear_program(df, n_selection, budget)


# Read data
df_tourpool, df_results = read_data()

# Parameters
month_multipliers = {
    'January': 0,
    'February': 1,
    'March': 1,
    'April': 1,
    'May': 2,
    'June': 2,
    'July': 0,
    'August': 0,
    'September': 0,
    'October': 0,
    'November': 0,
    'December': 0,
}

points = 'PCS'
metric = 'mean'
n_selection = 15
budget = 100

run_tourpool(df_tourpool, df_results, points, metric, n_selection, budget, month_multipliers)
