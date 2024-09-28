import streamlit as st
import pandas as pd
import altair as alt

from utils.date_time import add_minutes_to_time, get_time_windows
from utils.indicator import turnover_ratio

# Turnover Ratio Calculation Function
def calculate_turnover_ratios(transactions_df, balances_df, opening_time, closing_time, processing_window, num_days):
    # Create an empty list to store the results
    results = []

    # Loop through each day of the simulation
    for day in range(1, num_days + 1):
        # Get the time windows for the day
        time_windows = get_time_windows(opening_time, closing_time, processing_window)
        
        # For each time window, calculate the turnover ratio
        for i, time_window in enumerate(time_windows):
            # Filter transactions up to the current time window
            filtered_transactions = transactions_df[
                (transactions_df['day'] == day) & 
                (transactions_df['time'] <= time_window) & 
                (transactions_df['status'] == 'Success')
            ]
            
            # Sum of all successful payments settled
            total_payments_settled = filtered_transactions['amount'].sum()
            
            # Filter balances up to the current time window
            filtered_balances = balances_df[
                (balances_df['day'] == day) & 
                (balances_df['time'] <= time_window)
            ]
            
            # Average liquidity (sum of all balances divided by number of periods passed)
            periods_passed = i + 1
            average_liquidity = filtered_balances['balance'].sum() / periods_passed
            
            # Calculate turnover ratio for the current period
            turnover = turnover_ratio(total_payments_settled, average_liquidity)
            
            # Append results to the list
            results.append({
                'day': day,
                'time': time_window,
                'turnover_ratio': turnover
            })

    # Convert the results list to a DataFrame
    turnover_df = pd.DataFrame(results)

    return turnover_df

st.markdown("# Liquidity Results")

# establish relevant variables
transactions_df = st.session_state['Log Files']['Processed Transactions']
balances_df = st.session_state['Log Files']['Account Balance']
opening_time = st.session_state['Parameters']['Opening Time']
closing_time = st.session_state['Parameters']['Closing Time']
processing_window = st.session_state['Parameters']['Processing Window']
num_days = st.session_state['Parameters']['Number of Days']

st.markdown("## Turnover Ratio")

# calculate turnover ratios
turnover_ratios_df = calculate_turnover_ratios(
    transactions_df, 
    balances_df, 
    opening_time, 
    closing_time, 
    processing_window, 
    num_days
)
# plot ratios
# Step 1: Combine day and time into a single column for better x-axis representation
turnover_ratios_df['period'] = turnover_ratios_df['day'].astype(str) + ' ' + turnover_ratios_df['time']
# Step 2: Sort the dataframe by day and time to ensure proper ordering
turnover_ratios_df = turnover_ratios_df.sort_values(by=['day', 'time'])
# Step 3: Use Altair for plotting
base_chart = alt.Chart(turnover_ratios_df).mark_line().encode(
    x=alt.X('time:N', title='Time', axis=alt.Axis(labelAngle=0)),  # Time on x-axis
    y=alt.Y('turnover_ratio:Q', title='Turnover Ratio'),  # Turnover ratio on y-axis
    color='day:N',  # Different colors for different days
    tooltip=['day', 'time', 'turnover_ratio']
).properties(
    width=150,  # Adjusting width for each individual facet
    height=400  # Set height for the chart
)
# Facet the chart by 'day'
facet_chart = base_chart.facet(
    column=alt.Column('day:N', title='Day')  # Separate columns for each day
)
# Step 4: Display the chart using Streamlit
st.altair_chart(facet_chart, use_container_width=True)


st.markdown("## Average Payment Delay")