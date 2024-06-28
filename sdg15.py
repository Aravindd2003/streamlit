import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import tkinter
window=tkinter.Tk();
window.geometry('400x300')
bt=tkinter.Button(window,text='target value',bg='red',fg='black')
bt.grid(column=1,row=1)
window.mainloop()
st.title("Dashboard")

@st.cache_data
def load_data(path: str):
    data = pd.read_excel(path)
    return data

# Load the data
df = load_data("sdg15.xlsx")

st.sidebar.header("Select your choice:")

# Get the year columns (assuming they start from the 5th column and end 3 columns before the end)
years = df.columns[4:-1]

# User input for indicator selection
indicator = st.sidebar.multiselect("Pick your department:", df["Indicator"].unique())
if not indicator:
    df1 = df.copy()
else:
    df1 = df[df["Indicator"].isin(indicator)]

# User input for subcategory selection
subcategory = st.sidebar.multiselect("Pick your category:", df1["Sub Category"].unique())
if not subcategory:
    df2 = df1.copy()
else:
    df2 = df1[df1["Sub Category"].isin(subcategory)]

# Check if 'Target Value' column is present
if 'Target Value' not in df2.columns:
    st.error("Column 'Target Value' not found in the data.")
else:
    # Ensure that 'Target Value' is numeric
    df2['Target Value'] = pd.to_numeric(df2['Target Value'], errors='coerce')

    # Melt the data to long format
    melted_df = df2.melt(id_vars=["Indicator", "Sub Category", "Target Value"],
                         value_vars=years,
                         var_name="Year",
                         value_name="Yearly Value")

    # Add a column for performance status
    def performance_status(row):
        if pd.isna(row["Yearly Value"]) or pd.isna(row["Target Value"]):
            return "No Data"
        elif row["Yearly Value"] < row["Target Value"]:
            return "Need to Improve"
        elif row["Yearly Value"] == row["Target Value"]:
            return "Completed"
        elif row["Yearly Value"] > row["Target Value"]:
            return "Going to Next Level"
        else:
            return "Proceeding"

    melted_df["Status"] = melted_df.apply(performance_status, axis=1)

    # Define color mapping for the statuses
    color_mapping = {
        "Need to Improve": "red",
        "Proceeding": "orange",
        "Completed": "green",
        "Going to Next Level": "green",
        "No Data": "gray"
    }

    # Create the bar graph
    fig = px.bar(melted_df,
                 x="Year",
                 y="Yearly Value",
                 color="Status",
                 color_discrete_map=color_mapping,
                 title="Yearly Performance vs Target",
                 labels={"Yearly Value": "Value", "Year": "Year", "Status": "Performance Status"})

    # Add target line
    for target in df2['Target Value'].unique():
        fig.add_hline(y=target, line_dash="dash", line_color="black", annotation_text=f"Target: {target}",
                      annotation_position="right")

        # Adjust the layout for better visibility
    fig.update_layout(height=600, width=1000, yaxis=dict(title='Yearly Value'), xaxis=dict(title='Year'))

    # Display the chart
    st.plotly_chart(fig)

    # Line Chart for Yearly Trends
    fig_line = px.line(melted_df, x="Year", y="Yearly Value", color="Indicator", markers=True,
                       title="Yearly Trend for Selected Indicators",
                       labels={"Yearly Value": "Value", "Year": "Year", "Indicator": "Indicator"})
    st.plotly_chart(fig_line)

    # Pie Chart for Performance Status
    status_counts = melted_df["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig_pie = px.pie(status_counts, values="Count", names="Status", title="Performance Status Distribution")
    st.plotly_chart(fig_pie)

    heatmap_data = melted_df.pivot_table(index="Indicator", columns="Year", values="Yearly Value", aggfunc="mean")

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis'
    ))

    fig_heatmap.update_layout(title="Category Performance Heatmap", xaxis_title="Year", yaxis_title="Indicator")
    st.plotly_chart(fig_heatmap)


