import streamlit as st
import requests
import pandas as pd
import datetime
import folium
from streamlit_folium import folium_static

# API URLs
COMPLETES_URL = "https://api-db.sota.org.uk/admin/sota_completes_by_id?id=46844&desc=0&year=all"
SUMMITS_URL = "https://sotl.as/api/regions/GM/ES"

# Fetch user completes
def get_completed_summits():
    response = requests.get(COMPLETES_URL)
    if response.status_code == 200:
        return {summit["SummitCode"] for summit in response.json()}
    return set()

# Fetch all summits and filter valid ones
def get_valid_summits():
    response = requests.get(SUMMITS_URL)
    if response.status_code == 200:
        today = datetime.datetime.now(datetime.timezone.utc).isoformat()
        summits = [s for s in response.json() if s["validTo"] > today]
        return summits
    return []

# Find missing summits
def get_missing_summits():
    completed = get_completed_summits()
    all_summits = get_valid_summits()
    return [s for s in all_summits if s["code"] not in completed]

# Streamlit UI
st.set_page_config(layout='centered', page_title="wenseth complete💯", page_icon=":100:")
st.image("logo.png")

missing_summits = get_missing_summits()
if not missing_summits:
    st.success("You've completed all GM/ES summits! 🥳")
    st.balloons()
else:
    df = pd.DataFrame([
        {
            "Summit": s["name"],
            "Code": s["code"],
            "Latitude": s["coordinates"]["latitude"],
            "Longitude": s["coordinates"]["longitude"],
            "Altitude": s["altitude"],
            "Points": s["points"]
        }
        for s in missing_summits
    ])

    valid_summits = get_valid_summits()
    completed_count = len(valid_summits) - len(missing_summits)

    col1, col2 = st.columns(2)
    col1.metric("Completed", value=completed_count, border=True)
    col2.metric("Remaining", value=len(missing_summits), border=True)

    # Display map with folium
    m = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=8)
    for _, row in df.iterrows():

        popup = f"""<b>{row['Summit']}</b><br><a href="https://sotl.as/summits/{row['Code']}" target="_blank">{row['Code']}</a><br>Points: {row['Points']}"""

        tooltip = row['Summit']

        tooltip = f"<b>{row['Summit']}</b><br>Points: {row['Points']}"

        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color="lightgreen" if row["Points"] == 1 else "green" if row["Points"] ==2 else "darkgreen" if row["Points"] == 4 else "orange" if row["Points"] == 6 else "darkred" if row["Points"] == 8 else "red")
        ).add_to(m)

    folium_static(m,
    height=600,
    width=700,
    )

    st.dataframe(df, hide_index=True, column_order=("Summit", "Code", "Altitude", "Points"))

    st.header("🎩🗣📢 Get cracking GM/ES boys! 🥾")
