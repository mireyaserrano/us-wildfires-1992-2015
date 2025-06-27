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
    This interactive dashboard visualizes 23 years of U.S. wildfire data—revealing when, where, and why fires occur.
    Each chart helps uncover trends in fire count, cause, duration, and size by state, so you can better understand the patterns and take steps to stay safe, aware, and engaged.
    </h5>
    """,
    unsafe_allow_html=True
)
st.markdown("#### Some Questions to Consider")
st.markdown("""
- Do human activities or natural factors lead to more damaging fire behavior? (Consider population density!)
- Which regions of the U.S. are persistently vulnerable to wildfire outbreaks?
- How has the geographic distribution shifted over time?
            """)

st.markdown("---")


@st.cache_data
def load_data():
    return pd.read_csv("Full_Wildfire_Dataset__1992_2015_.csv", parse_dates=["DISCOVERY_DATE", "CONTAINMENT_DATE"])

data = load_data()


# Sidebar: So What?
st.sidebar.title("Why This Matters")

with st.sidebar.expander("🔥Wildfires Affect More Than Just Burned Land"):
    st.markdown("""
Even if you're far from a fire zone, wildfires can impact:

- **Air quality**, even hundreds of miles away  
- **Water supply**, as watersheds are damaged by runoff and ash  
- **Energy infrastructure**, causing blackouts or utility failures  
- **Transportation and communication systems**  
- **Homes, livelihoods, and community health**
    """)

st.sidebar.markdown("""
For those living in fire-prone regions, preparation can be ***lifesaving!***  
                    
For others, understanding wildfire risks helps promote **smarter land use**, **public safety planning**, and **climate resilience**.
""")


st.sidebar.markdown("### 📣 What You Can Do")

st.sidebar.markdown("""
- Learn your local fire risk  
- Make an evacuation plan  
- Support fire prevention efforts  
- Stay informed during fire season
""")

with st.sidebar.expander("🧭 Emergency & Education Resources"):
    st.markdown("""
- [Red Cross Wildfire Safety Guide](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/wildfire.html)  
- [Red Cross: How to Prevent Wildfires](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/wildfire/how-to-prevent-wildfires.html)  
- [Ready.gov Wildfires](https://www.ready.gov/wildfires)  
- [AirNow Fire & Smoke Map](https://fire.airnow.gov/)  
    """)
with st.sidebar.expander("📌 Final Notes & Key Takeaways"):
    st.markdown("""
    - **Fire Activity Is Highly State-Dependent**: States like California, Texas, and Georgia consistently report high wildfire counts across the years. Interacting with the state bar chart reveals stark differences between neighboring states.
    
    - **Human Activity Dominates Causes**: Exploring the strip plot shows that many long-duration fires stem from human-related causes such as debris burning, equipment use, or arson—especially in populated states.

    - **Fire Size Varies Widely by Cause**: The box plot reveals that lightning-caused fires often result in some of the largest acreage burned, likely due to their occurrence in remote or unmanaged areas.

    - **Temporal Trends Show Fluctuations and Clusters**: The line chart exposes periodic spikes in fire counts (e.g., around drought years), and lets users identify how some states experience more volatility over time than others.
    """)

with st.sidebar.expander("ℹ️ About the Dataset"):
    st.markdown("""
This dashboard visualizes U.S. wildfire data from 1992 to 2015 based on records compiled by federal, state, and local fire organizations.

**Source**:  
Short, Karen C. 2022. *Spatial wildfire occurrence data for the United States, 1992–2020 [FPA_FOD_20221014]*.  
6th Edition. Fort Collins, CO: Forest Service Research Data Archive.  
[DOI: 10.2737/RDS-2013-0009.6](https://doi.org/10.2737/RDS-2013-0009.6)

**Note**:  
This dashboard uses a cleaned subset of the dataset (1992–2015) and focuses on trends in fire count, duration, size, and cause across U.S. states.
    """)

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

click_selection = alt.selection_point(fields=["STATE"], toggle=True, empty="none")

st.markdown("### Wildfires Across Time and States (1992–2015)")
st.markdown("""
Geographic patterns of wildfires reveal regional vulnerabilities and can reflect changes in climate, land use, or fire management policy.

*Use these interactive charts to explore which U.S. states experienced the most wildfires between 1992–2015. Click on a state bar to see its **yearly** trend in the linked charts below.*
    """)

# Bar Chart COUNT colored by STATE 
st.markdown("##### 🗺️ State-by-State Fire Count")
bar_chart = alt.Chart(state_counts).mark_bar().encode(
    x=alt.X("STATE:N", sort="ascending", title="US State"),
    y=alt.Y("Fire_Count:Q", title="Total Wildfires"),
    color=alt.Color("STATE:N", title="State"),
    tooltip=["STATE", "Fire_Count"],
    opacity=alt.condition(click_selection, alt.value(1), alt.value(0.25))
).add_params(
    click_selection
).properties(
    width=800,
    height=400
).interactive()

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
    title="📆 A Temporal View of Wildfires, 1992-2015"
)

st.caption("💡 Tip: Hold `Shift` and click multiple bars to compare several states at once. (If examining smaller states, zooming may be helpful!)")

st.altair_chart(bar_chart & line_chart, use_container_width=True)


# Cause vs. Size/Duration 
st.markdown("### What Sparks a Wildfire—and What Makes It Last?")
st.markdown("""
Wildfires begin for many reasons—but not all causes are equal. Some result in fast, containable burns.
Others rage for days and spread across vast terrain.

These next two charts reveal how **cause** relates to both **fire duration** and **fire size**. Use the dropdown to explore patterns in a given state.
""")

# Adding DURATION_DAYS column
data["DURATION_DAYS"] = (data["CONTAINMENT_DATE"] - data["DISCOVERY_DATE"]).dt.days
data = data.dropna(subset=["DURATION_DAYS", "FIRE_SIZE", "STAT_CAUSE_DESCR"])
data = data[data["DURATION_DAYS"] >= 0]

# Dropdown to select a state
state_options = sorted(data["STATE"].dropna().unique())

selected_state = st.selectbox("Select a state to filter by:", options=state_options, index=state_options.index("CA"))

st.markdown(f"##### ⏱️🔥 Explore Wildfire Duration vs. Cause in **{selected_state}**")

# Filtering data:
scatter_data = data[data["STATE"] == selected_state]


st.markdown("**Try** identifying which causes are associated with prolonged fire events and explore how that varies by state.")

st.caption("*Hover over points to see specific fire names, counties, and sizes.*") 

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

st.markdown(f"##### 📏🔥 Explore Wildfire Size vs. Cause in **{selected_state}**")
st.markdown("**Try** identifying which causes are linked to especially large wildfires—and notice which ones tend to stay small. What patterns emerge across different states?")

st.caption(f"*A **logarithmic y-axis** helps visualize variation across small and massive fires. Some causes may lead to fewer—but far larger—fires.*")

box_plot = alt.Chart(scatter_data).mark_boxplot(extent="min-max").encode(
    x=alt.X("STAT_CAUSE_DESCR:N", title="Cause", sort="-y", axis=alt.Axis(labelAngle=-90)),
    y=alt.Y("FIRE_SIZE:Q", title="Acres Burned", scale=alt.Scale(type="log")),  # Log scale for clarity
    color=alt.Color("STAT_CAUSE_DESCR:N", legend=None)
).properties(
    width=900,
    height=400,
    title=f"Distribution of Fire Sizes by Cause ({selected_state})"
).interactive()

st.altair_chart(box_plot, use_container_width=True)

# st.caption("Make sure to check out the Resources and Final Takeaways sections in the sidebar! Stay Safe!")