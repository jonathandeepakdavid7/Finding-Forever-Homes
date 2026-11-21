import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# 1. App setup and data loading
# Configure the Streamlit application
st.set_page_config(
    page_title="Finding Forever Homes",
    page_icon="🐾",
    layout="wide"
)

# Load the cleaned animal shelter dataset
@st.cache_data
def load_data():
    data_path = Path(__file__).with_name("animal_shelter_clean.csv")

    data = pd.read_csv(
        data_path,
        parse_dates=["Outcome Date"]
    )

    data["Year"] = data["Outcome Date"].dt.year

    data["Is Adoption"] = (
        data["Outcome Type Clean"] == "Adoption"
    )

    return data


df = load_data()

# 2. Introduction and interactive filters
# Application introduction
st.title("🐾 Finding Forever Homes")
st.subheader("Adoption Patterns at the Austin Animal Center")

st.write(
    "Explore how recorded adoption outcomes differed "
    "between dogs and cats from 2019 through 2024."
)

st.info(
    "Adoption share represents the percentage of known "
    "shelter outcomes classified as Adoption. "
    "It does not represent an individual animal's "
    "probability of being adopted."
)

# Interactive sidebar filters
st.sidebar.header("Explore the Data")

year_range = st.sidebar.slider(
    "Select years",
    min_value=2019,
    max_value=2024,
    value=(2019, 2024)
)

animal_selection = st.sidebar.multiselect(
    "Select animal types",
    options=["Cat", "Dog"],
    default=["Cat", "Dog"]
)

# Apply filters
filtered_df = df[
    df["Year"].between(*year_range) &
    df["Animal Type"].isin(animal_selection)
].copy()

if filtered_df.empty:
    st.warning("Please select at least one animal type.")
    st.stop()

# 3. Overview and central finding
# Display summary metrics
st.header("Shelter Outcomes Overview")

col1, col2, col3 = st.columns(3)

total_outcomes = len(filtered_df)
total_adoptions = filtered_df["Is Adoption"].sum()

adoption_share = (
    total_adoptions / total_outcomes * 100
)

col1.metric("Known Outcomes", f"{total_outcomes:,}")
col2.metric("Adoptions", f"{total_adoptions:,}")
col3.metric("Adoption Share", f"{adoption_share:.2f}%")

# Put the most important verified comparison near the beginning of the story.
# Use the current filters so the text never contradicts the charts.
st.subheader("The Story Behind the Numbers")

story_summary = (
    filtered_df.groupby("Year")
    .agg(
        Known_Outcomes=("Is Adoption", "size"),
        Adoptions=("Is Adoption", "sum")
    )
    .reset_index()
    .sort_values("Year")
)
story_summary["Adoption Share"] = (
    story_summary["Adoptions"] / story_summary["Known_Outcomes"] * 100
)

if len(story_summary) >= 2:
    first = story_summary.iloc[0]
    last = story_summary.iloc[-1]
    share_change = last["Adoption Share"] - first["Adoption Share"]
    count_change = int(last["Adoptions"] - first["Adoptions"])

    st.write(
        f"**Key finding ({int(first['Year'])}–{int(last['Year'])}):** "
        f"Adoption share moved from {first['Adoption Share']:.2f}% "
        f"to {last['Adoption Share']:.2f}% "
        f"({share_change:+.2f} percentage points). "
        f"Recorded adoptions changed from {int(first['Adoptions']):,} "
        f"to {int(last['Adoptions']):,} "
        f"({count_change:+,} outcomes)."
    )

    if share_change > 0 and count_change < 0:
        st.write(
            "**Why it matters:** A larger share of recorded outcomes were "
            "adoptions even though the number of adoptions fell. "
            "Shelter supporters should consider counts and percentages together "
            "before drawing conclusions."
        )
    else:
        st.write(
            "**Why it matters:** Comparing the percentage and number of "
            "adoptions shows whether the two measures tell the same story. "
            "Both are useful context for shelter volunteers and supporters."
        )
else:
    only_year = int(story_summary.iloc[0]["Year"])
    st.write(
        f"**{only_year} snapshot:** "
        f"{total_adoptions:,} of {total_outcomes:,} recorded known outcomes "
        f"were adoptions ({adoption_share:.2f}%). "
        "Select multiple years to explore how this changed over time."
    )


# 4. Adoption-share trends over time
# Calculate annual adoption shares
st.header("How Have Adoption Shares Changed Over Time?")

annual = (
    filtered_df.groupby(["Year", "Animal Type"])
    .agg(
        Known_Outcomes=("Is Adoption", "size"),
        Adoptions=("Is Adoption", "sum")
    )
    .reset_index()
)

annual["Adoption Share (%)"] = (
    annual["Adoptions"] /
    annual["Known_Outcomes"] * 100
)

# Create the interactive Plotly chart
fig = px.line(
    annual,
    x="Year",
    y="Adoption Share (%)",
    color="Animal Type",
    markers=True,
    color_discrete_map={
        "Dog": "#3978A8",
        "Cat": "#D58E47"
    },
    custom_data=["Adoptions", "Known_Outcomes"]
)

fig.update_traces(
    hovertemplate=(
        "Year: %{x}<br>"
        "Adoption share: %{y:.2f}%<br>"
        "Adoptions: %{customdata[0]:,}<br>"
        "Known outcomes: %{customdata[1]:,}"
        "<extra>%{fullData.name}</extra>"
    )
)

fig.update_layout(
    template="plotly_white",
    height=480,
    xaxis_title="Year",
    yaxis_title="Adoption Share (%)",
    legend_title_text="Animal Type"
)

# Show only years included in the selected data
fig.update_xaxes(
    tickmode="array",
    tickvals=sorted(annual["Year"].unique()),
    range=[
        annual["Year"].min() - 0.5,
        annual["Year"].max() + 0.5
    ]
)

fig.update_yaxes(range=[0, 100], ticksuffix="%")

st.plotly_chart(fig, use_container_width=True)

# 5. Adoption shares by age group

st.divider()

st.header("How Does Adoption Share Differ by Age?")

st.write(
    "Compare recorded adoption shares across four age groups "
    "for dogs and cats. The chart responds to the selected "
    "year range and animal types."
)

# Define the age-group order
age_order = [
    "Under 1 year",
    "1–2 years",
    "3–6 years",
    "7+ years"
]

# Exclude invalid ages only from this comparison
age_filtered = filtered_df.dropna(
    subset=["Age Group"]
).copy()

# Calculate adoption shares by age group
age_summary = (
    age_filtered
    .groupby(["Animal Type", "Age Group"])
    .agg(
        Known_Outcomes=("Is Adoption", "size"),
        Adoptions=("Is Adoption", "sum")
    )
    .reset_index()
)

age_summary["Adoption Share (%)"] = (
    age_summary["Adoptions"] /
    age_summary["Known_Outcomes"] * 100
)

# Create the interactive grouped bar chart
fig_age = px.bar(
    age_summary,
    x="Age Group",
    y="Adoption Share (%)",
    color="Animal Type",
    barmode="group",
    category_orders={"Age Group": age_order},
    color_discrete_map={
        "Dog": "#3978A8",
        "Cat": "#D58E47"
    },
    text="Adoption Share (%)",
    custom_data=["Known_Outcomes", "Adoptions"]
)

# Add percentage labels and hover information
fig_age.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    hovertemplate=(
        "Age group: %{x}<br>"
        "Adoption share: %{y:.2f}%<br>"
        "Known outcomes: %{customdata[0]:,}<br>"
        "Adoptions: %{customdata[1]:,}"
        "<extra>%{fullData.name}</extra>"
    )
)

# Improve readability
fig_age.update_layout(
    template="plotly_white",
    font=dict(size=15),
    height=500,
    xaxis_title="Age Group",
    yaxis_title="Adoption Share (%)",
    legend_title_text="Animal Type"
)

fig_age.update_yaxes(
    range=[0, 100],
    ticksuffix="%"
)

st.plotly_chart(fig_age, use_container_width=True)

# Explain age-data limitations
excluded_ages = len(filtered_df) - len(age_filtered)

st.caption(
    f"Age comparison uses {len(age_filtered):,} records "
    f"with valid ages. {excluded_ages:,} records with "
    f"invalid or missing ages are excluded from this chart."
)

# 6. Recorded outcome categories

st.divider()

st.header("How Do Shelter Outcomes Differ Between Dogs and Cats?")

st.write(
    "Adoption is only one type of shelter outcome. "
    "This chart compares the distribution of adoptions, "
    "transfers, returns to owners, and other outcomes "
    "for the selected animals and years."
)

# Group less common outcomes for readability
main_categories = [
    "Adoption",
    "Transfer",
    "Return to Owner"
]

outcome_filtered = filtered_df.copy()

outcome_filtered["Outcome Category"] = (
    outcome_filtered["Outcome Type Clean"].where(
        outcome_filtered["Outcome Type Clean"].isin(
            main_categories
        ),
        "Other Recorded Outcomes"
    )
)

# Calculate outcome counts
outcome_app_summary = (
    outcome_filtered
    .groupby(["Animal Type", "Outcome Category"])
    .size()
    .reset_index(name="Outcome Count")
)

# Calculate total outcomes for each animal type
outcome_app_summary["Total Outcomes"] = (
    outcome_app_summary
    .groupby("Animal Type")["Outcome Count"]
    .transform("sum")
)

# Calculate percentages
outcome_app_summary["Outcome Share (%)"] = (
    outcome_app_summary["Outcome Count"] /
    outcome_app_summary["Total Outcomes"] * 100
)

# Create the interactive chart
fig_outcome_app = px.bar(
    outcome_app_summary,
    x="Outcome Share (%)",
    y="Animal Type",
    color="Outcome Category",
    orientation="h",
    title="Distribution of Shelter Outcomes",
    category_orders={
        "Animal Type": ["Dog", "Cat"],
        "Outcome Category": [
            "Adoption",
            "Transfer",
            "Return to Owner",
            "Other Recorded Outcomes"
        ]
    },
    color_discrete_map={
        "Adoption": "#2E7D32",
        "Transfer": "#7E57C2",
        "Return to Owner": "#E69F00",
        "Other Recorded Outcomes": "#9E9E9E"
    },
    custom_data=["Outcome Count", "Total Outcomes"]
)

# Add hover information
fig_outcome_app.update_traces(
    hovertemplate=(
        "Share: %{x:.2f}%<br>"
        "Outcome count: %{customdata[0]:,}<br>"
        "Total known outcomes: %{customdata[1]:,}"
        "<extra>%{fullData.name}</extra>"
    )
)

# Improve appearance
fig_outcome_app.update_layout(
    template="plotly_white",
    barmode="stack",
    font=dict(size=15),
    height=450,
    xaxis_title="Share of Known Outcomes (%)",
    yaxis_title="Animal Type",
    legend_title_text="Outcome Category"
)

fig_outcome_app.update_xaxes(
    range=[0, 100],
    dtick=20,
    ticksuffix="%"
)

st.plotly_chart(
    fig_outcome_app,
    use_container_width=True
)

st.caption(
    "Less frequent outcome categories are grouped as "
    "'Other Recorded Outcomes' for readability. "
    "Percentages are calculated separately for each "
    "animal type using known outcomes."
)

# 7. Annual outcome volume (counts)

st.divider()

st.header("How Has Shelter Outcome Volume Changed Over Time?")

st.write(
    "Adoption percentages tell only part of the story. "
    "This chart shows how many known dog and cat outcomes "
    "were recorded each year. Comparing counts with adoption "
    "shares helps us avoid misleading conclusions."
)

# Calculate annual outcome counts and adoptions
annual_volume_app = (
    filtered_df
    .groupby(["Year", "Animal Type"])
    .agg(
        Known_Outcomes=("Is Adoption", "size"),
        Adoptions=("Is Adoption", "sum")
    )
    .reset_index()
)

annual_volume_app = annual_volume_app.rename(
    columns={"Known_Outcomes": "Known Outcomes"}
)

# Create grouped bar chart
fig_volume_app = px.bar(
    annual_volume_app,
    x="Year",
    y="Known Outcomes",
    color="Animal Type",
    barmode="group",
    title="Annual Shelter Outcome Volume (2019–2024)",
    color_discrete_map={
        "Dog": "#3978A8",
        "Cat": "#D58E47"
    },
    text="Known Outcomes",
    custom_data=["Adoptions"]
)

# Improve hover information and labels
fig_volume_app.update_traces(
    texttemplate="%{text:,}",
    textposition="outside",
    hovertemplate=(
        "Year: %{x}<br>"
        "Known outcomes: %{y:,}<br>"
        "Adoptions: %{customdata[0]:,}"
        "<extra>%{fullData.name}</extra>"
    )
)

# Improve appearance
fig_volume_app.update_layout(
    template="plotly_white",
    font=dict(size=15),
    height=520,
    xaxis_title="Year",
    yaxis_title="Number of Known Outcome Records",
    legend_title_text="Animal Type",
    bargap=0.2
)

fig_volume_app.update_xaxes(
    tickmode="array",
    tickvals=sorted(annual_volume_app["Year"].unique()),
    range=[
        annual_volume_app["Year"].min() - 0.5,
        annual_volume_app["Year"].max() + 0.5
    ]
)
fig_volume_app.update_yaxes(
    rangemode="tozero",
    tickformat=","
)

st.plotly_chart(
    fig_volume_app,
    use_container_width=True
)

st.caption(
    "Counts represent recorded shelter outcomes, "
    "not necessarily unique animals. The chart responds "
    "to the selected years and animal types."
)




# 8. Conclusions and limitations

st.divider()
st.header("What Can Shelter Supporters Learn?")

# Present full-period findings only when all data is selected
if year_range == (2019, 2024) and set(animal_selection) == {"Cat", "Dog"}:

    st.write(
        "**Age-related differences:** Dogs under one year had a "
        "65.24% adoption share, compared with 37.20% for dogs "
        "aged seven or older. This difference suggests that "
        "outcomes for older dogs deserve closer attention."
    )

    st.write(
        "**Different outcome patterns:** Cats had a higher "
        "transfer share (32.49%), while dogs had a higher "
        "return-to-owner share (18.11%, compared with 3.37% "
        "for cats). These differences highlight the importance "
        "of examining outcomes beyond adoption alone."
    )

else:
    st.write(
        "The selected data reveal differences in adoption "
        "shares, animal age groups, and outcome categories. "
        "Use the charts above to identify which patterns "
        "deserve further investigation."
    )

st.write(
    "**Why it matters:** Shelter volunteers and animal welfare "
    "supporters can use these comparisons to ask more focused "
    "questions about different animal populations and "
    "shelter outcomes."
)

st.write(
    "**Important limitation:** These records describe shelter "
    "outcomes, not necessarily unique animals or every animal "
    "entering the shelter. The data show patterns and "
    "associations but do not establish their causes."
)
