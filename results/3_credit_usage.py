import altair as alt
import streamlit as st


# Section Header
st.markdown("## Credit Usage")

# Load the Credit Facility log from session state
df_credit = st.session_state['Log Files']['Credit Facility']

# Prepare the DataFrame by sorting it for time-series plotting
df_credit = df_credit.sort_values(by=['day', 'time'])

# Rename the column for better readability
df_credit = df_credit.rename(columns={"total_credit": "Total Credit Usage"})

# Define the base chart
base_chart = alt.Chart(df_credit).mark_line().encode(
    x=alt.X('time:N', title='Time', axis=alt.Axis(labelAngle=0)),  # Time on the x-axis
    y=alt.Y('Total Credit Usage:Q', title='Total Credit Usage'),  # Total Credit Usage on the y-axis
    color='day:N',  # Use different colors for different days
    tooltip=['day', 'time', 'Total Credit Usage']  # Tooltips for detailed info
).properties(
    width=800,  # Set the width of the chart
    height=400  # Set the height of the chart
)

# Facet the chart by day for better visualization
facet_chart = base_chart.facet(
    column=alt.Column('day:N', title='Day')  # Create a column for each day
)

# Display the chart in Streamlit
st.altair_chart(facet_chart, use_container_width=True)