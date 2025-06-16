import streamlit as st
import pandas as pd
import altair as alt

# App setup
st.set_page_config(layout="wide")
st.title("Burning Across America: A Visual History of U.S. Wildfires (1992–2015)")
st.markdown(
    """
    <h5 style='color:gray; font-weight:normal;'>
    Wildfires are increasing in frequency and intensity across the U.S.—but not all fires are the same.<br>
    This interactive dashboard visualizes 23 years of wildfire data to help you uncover trends in fire count, cause, duration, and size by state.
    </h5>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    return pd.read_csv("Full_Wildfire_Dataset__1992_2015_.csv", parse_dates=["DISCOVERY_DATE", "CONTAINMENT_DATE"])

data = load_data()

# Define U.S. Census sub-region mapping
region_map = {
    "Pacific": ["AK", "CA", "HI", "OR", "WA"],
    "Mountain": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],
    "West South Central": ["AR", "LA", "OK", "TX"],
    "East South Central": ["AL", "KY", "MS", "TN"],
    "South Atlantic": ["DE", "DC", "FL", "GA", "MD", "NC", "SC", "VA", "WV"],
    "West North Central": ["IA", "KS", "MN", "MO", "NE", "ND", "SD"],
    "East North Central": ["IL", "IN", "MI", "OH", "WI"],
    "Mid-Atlantic": ["NJ", "NY", "PA"],
    "New England": ["CT", "ME", "MA", "NH", "RI", "VT"]
}
state_to_region = {state: region for region, states in region_map.items() for state in states}
data["REGION"] = data["STATE"].map(state_to_region)

# counting fires by state
state_counts = data.groupby(["STATE"]).size().reset_index(name="Fire_Count")

# Multi on state field
# click_selection = alt.selection_multi(fields=["STATE"], empty="none")

click_selection = alt.selection_point(fields=["STATE"], toggle=True, empty="none")

st.markdown(
    """**Wildfires Across States and Time (1992–2015)**

    """)
# Bar Chart colored by STATE 
bar_chart = alt.Chart(state_counts).mark_bar().encode(
    x=alt.X("STATE:N", sort="ascending", title="US State"),
    y=alt.Y("Fire_Count:Q", title="Total Wildfires"),
    color=alt.Color("STATE:N", title="State"),
    tooltip=["STATE", "Fire_Count"],
    opacity=alt.condition(click_selection, alt.value(1), alt.value(0.5))
).add_params(
    click_selection
).properties(
    width=800,
    height=400
)

# Line Chart for Yearly Trends 
yearly_trends = data.groupby(["FIRE_YEAR", "STATE"]).size().reset_index(name="Fire_Count")

line_chart = alt.Chart(yearly_trends).mark_line(point=True).encode(
    x=alt.X("FIRE_YEAR:O", title="Year"),
    y=alt.Y("Fire_Count:Q", title="Wildfires"),
    color=alt.Color("STATE:N", title="State"),
    tooltip=["FIRE_YEAR", "STATE", "Fire_Count"]
).transform_filter(
    click_selection
).properties(
    width=800,
    height=300,
    title="Wildfires Through 1992-2015"
)

# instruction and info
st.markdown("""
*Geographic patterns of wildfires reveal regional vulnerabilities and can reflect changes in climate, land use, or fire management policy.*

Use this interactive chart to explore which U.S. states experienced the most wildfires between 1992–2015.  
Click on a state bar to reveal **yearly trends** below.
    """)
st.caption("💡 Tip: Hold `Shift` and click multiple bars to compare several states at once.")

st.altair_chart(bar_chart & line_chart, use_container_width=True)


# Cause vs. Size/Duration 

st.markdown("### 🔍 Explore Wildfire Duration vs. Cause")
st.markdown("Select a state to explore what causes long, large fires.")

# Adding DURATION_DAYS column
data["DURATION_DAYS"] = (data["CONTAINMENT_DATE"] - data["DISCOVERY_DATE"]).dt.days
data = data.dropna(subset=["DURATION_DAYS", "FIRE_SIZE", "STAT_CAUSE_DESCR"])
data = data[data["DURATION_DAYS"] >= 0]

# Dropdown to select a state
state_options = ["All States"] + sorted(data["STATE"].dropna().unique())

selected_state = st.selectbox("Select a state to filter by:", options=state_options, index=state_options.index("CA"))

# Filtering data:
scatter_data = data if selected_state == "All States" else data[data["STATE"] == selected_state]


st.markdown(f"""
This chart shows how long wildfires last based on their reported cause in **{selected_state}**.  

*Hover over points to see specific fire names, counties, and sizes.*  
**Try** identifying which causes are associated with prolonged fire events and explore how that varies by state.
    """)

# strip plot chart:
strip = alt.Chart(scatter_data).mark_circle(size=40, opacity=0.5).encode(
    y=alt.Y("STAT_CAUSE_DESCR:N", title="Cause", sort="-x"),
    x=alt.X("DURATION_DAYS:Q", title="Duration (Days)", scale=alt.Scale(zero=False)),
    color=alt.Color("STAT_CAUSE_DESCR:N", legend=None),
    tooltip=["FIRE_NAME", "COUNTY", "FIRE_YEAR", "FIRE_SIZE", "DURATION_DAYS"]
).properties(
    width=900,
    height=400,
    title=f"Distribution of Fire Durations by Cause ({selected_state})"
).interactive()

st.altair_chart(strip, use_container_width=True)

st.markdown("### Fire Size by Recorded Cause")
st.markdown("This chart shows the distribution of wildfire sizes (in acres) by cause, in the selected state.")
st.markdown(f"""
This chart compares how large wildfires become depending on their cause in **{selected_state}**.  
A **logarithmic y-axis** helps visualize variation across small and massive fires. Some causes may lead to fewer—but far larger—fires.
    """)
box_plot = alt.Chart(scatter_data).mark_boxplot(extent="min-max").encode(
    x=alt.X("STAT_CAUSE_DESCR:N", title="Cause", sort="-y", axis=alt.Axis(labelAngle=-45)),
    y=alt.Y("FIRE_SIZE:Q", title="Acres Burned", scale=alt.Scale(type="log")),  # Log scale for clarity
    color=alt.Color("STAT_CAUSE_DESCR:N", legend=None)
).properties(
    width=900,
    height=400,
    title=f"Distribution of Fire Sizes by Cause in {selected_state}"
).interactive()

st.altair_chart(box_plot, use_container_width=True)

with st.expander("Final Notes & Key Takeaways "):
    st.markdown("""
    - **Fire Activity Is Highly State-Dependent**: States like California, Texas, and Georgia consistently report high wildfire counts across the years. Interacting with the state bar chart reveals stark differences between neighboring states.
    
    - **Human Activity Dominates Causes**: Exploring the strip plot shows that many long-duration fires stem from human-related causes such as debris burning, equipment use, or arson—especially in populated states.

    - **Fire Size Varies Widely by Cause**: The box plot reveals that lightning-caused fires often result in some of the largest acreage burned, likely due to their occurrence in remote or unmanaged areas.

    - **Temporal Trends Show Fluctuations and Clusters**: The line chart exposes periodic spikes in fire counts (e.g., around drought years), and lets users identify how some states experience more volatility over time than others.
    """)



with st.expander("ℹ️ About the Dataset"):
    st.markdown("""
This dashboard visualizes U.S. wildfire data from 1992 to 2015 based on records compiled by federal, state, and local fire organizations.

**Source**:  
Short, Karen C. 2022. *Spatial wildfire occurrence data for the United States, 1992–2020 [FPA_FOD_20221014]*.  
6th Edition. Fort Collins, CO: Forest Service Research Data Archive.  
[DOI: 10.2737/RDS-2013-0009.6](https://doi.org/10.2737/RDS-2013-0009.6)

**Note**:  
This dashboard uses a cleaned subset of the dataset (1992–2015) and focuses on trends in fire count, duration, size, and cause across U.S. states.
    """)
