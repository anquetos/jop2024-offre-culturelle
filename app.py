import json
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from geopy import distance

from utils.folium_map import (
    create_folium_map,
    add_selected_site_marker,
    add_event_marker,
)


# ---------- Page configuration
st.set_page_config(
    page_title="JO Paris 2024 · Explorer",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Data loading functions


# Competition sites data
@st.cache_data
def load_competition_sites() -> pd.DataFrame:
    with open("datasets/jop2024-competition-sites.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index")
    df[["start_date", "end_date"]] = df[["start_date", "end_date"]].apply(
        pd.to_datetime
    )
    return df


# Events data
@st.cache_data
def load_events() -> pd.DataFrame:
    with open("datasets/jop2024-evenements.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index")
    df[["date_debut", "date_fin"]] = df[["date_debut", "date_fin"]].apply(
        pd.to_datetime
    )
    return df


#################
# Streamlit app #
#################

# Get and cache data
df_sites = load_competition_sites()
df_events = load_events()

st.title("JOP2024 et offre culturelle")
st.write(f"*Date et heure actuelle : {datetime.now().strftime('%d/%m/%Y - %H:%m')}*")

# --- Application : sidebar

with st.sidebar:
    st.subheader("Options")

    hide_sites = st.toggle(
        label="Masque les sites selon la date",
        help="Masque les sites où toutes les épreuves prévues se sont déjà déroulées.",
        value=False,
    )

    if hide_sites:
        df_sites = df_sites.loc[df_sites["end_date"].dt.date >= datetime.now().date()]

    games_type = st.radio(
        "Type de jeux", ["Olympiques", "Paralympiques"], horizontal=True
    )

    if games_type == "Olympiques":
        filtered_df = df_sites.loc[df_sites["games_type"] == "olympic"]
    else:
        filtered_df = df_sites.loc[df_sites["games_type"] == "paralympic"]

    events_distance = st.slider(
        label="Distance (km) des événements", max_value=20, value=2
    )

# with st.expander("DataFrame"):
#     st.dataframe(filtered_df)

# ---------- Application : main page

# Initialize sports list
sports_list = filtered_df["sports"].str.split(",", expand=True)
for col in sports_list.columns:
    sports_list[col] = sports_list[col].str.strip()
sports_list = sorted(set(sports_list.stack().values))

# Initialize selected sport
selected_sport = st.selectbox("Sélectionner un sport", options=sports_list)

# Get all available sites information for the selected sport
available_sites = filtered_df.loc[
    filtered_df["sports"].str.contains(selected_sport, regex=False)
].to_dict(orient="records")

# with st.expander("Results"):
#     st.write(available_sites)

site_selection_radio_label = (
    f"*{len(available_sites)} site(s) de compétition trouvé(s)* :"
)


def format_available_sites_information() -> list:
    if not available_sites:
        return []

    captions = []
    for site in available_sites:
        captions.append(
            f"**Sport(s) :** {site['sports']}\n\n"
            f"**Dates :** du {site['start_date'].strftime('%d/%m/%Y')} "
            f"au {site['end_date'].strftime('%d/%m/%Y')}"
        )
    return captions


selected_site = st.radio(
    label=site_selection_radio_label,
    options=available_sites,
    format_func=lambda x: x["nom_site"],
    captions=format_available_sites_information(),
)


# Compute distance between selected site and events and select events according to the 
# selected distance in sidebar options.
events = df_events.copy()
events["distance_km"] = events.apply(
    lambda x: distance.distance(
        [x["latitude"], x["longitude"]], [selected_site["lat"], selected_site["lon"]]
    ).km,
    axis="columns",
)
events = events.sort_values(by=["distance_km"])
events = events.loc[events["distance_km"] <= events_distance].to_dict(orient="records")


# st.write(events)

# Initialize Folium map
m = create_folium_map(location=[selected_site["lat"], selected_site["lon"]])

# Add a marker on the Folium map for the selected site
marker = add_selected_site_marker(site=selected_site)
marker.add_to(m)

# Add markers on the Folium map for the nearest events
for event in events:
    marker = add_event_marker(event=event)
    marker.add_to(m)

# Fit Folium map bounds to nearest events coordinates
m.fit_bounds([[event["latitude"], event["longitude"]] for event in events])

# Render Folium map
st_data = st_folium(m, use_container_width=True)

with st.expander("Session State"):
    st.write(st.session_state)
