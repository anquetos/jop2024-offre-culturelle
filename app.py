import json
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
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

# ---------- Functions


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


# Sports list
@st.cache_data
def generate_sports_list(df: pd.DataFrame) -> list:
    sports_list = df["sports"].str.split(",", expand=True)
    for col in sports_list.columns:
        sports_list[col] = sports_list[col].str.strip()
    sports_list = sorted(set(sports_list.stack().values))
    return sports_list


# Sites selection radio
@st.cache_data
def configure_sites_selection_radio_button(sites: dict) -> tuple[str, list]:
    if not sites:
        return ()

    label = f"*{len(sites)} site(s) de compétition trouvé(s)* :"

    captions = []
    for site in sites:
        captions.append(
            f"**Sport(s) :** {site['sports']}\n\n"
            f"**Dates :** du {site['start_date'].strftime('%d/%m/%Y')} "
            f"au {site['end_date'].strftime('%d/%m/%Y')}"
        )
    return (label, captions)


# Filtered events
@st.cache_data
def get_events_from_site_distance(
    df: pd.DataFrame, site_location: list, events_distance: float
) -> dict:
    df["distance_km"] = df.apply(
        lambda x: distance.distance([x["latitude"], x["longitude"]], site_location).km,
        axis="columns",
    )
    df = df.sort_values(by=["distance_km"])
    df = df.loc[df["distance_km"] <= events_distance].to_dict(orient="records")
    return df


# ---------- Initialize Session State values
if "sports_list" not in st.session_state:
    st.session_state["sports_list"] = []


# ---------- Get and cache data
df_sites = load_competition_sites()
df_events = load_events()


#################
# Streamlit app #
#################

st.title("JOP2024 et offre culturelle")
st.write(f"*Date et heure actuelle : {datetime.now().strftime('%d/%m/%Y - %H:%m')}*")

# ---------- Application : sidebar

with st.sidebar:
    st.subheader("Options")

    st.toggle(
        label="Masquer les sites selon la date",
        value=False,
        key="hide_sites_by_date",
        help="Masque les sites pour lesquels toutes les épreuves prévues se sont déjà déroulées.",
    )

    if st.session_state["hide_sites_by_date"]:
        df_sites = df_sites.loc[df_sites["end_date"].dt.date >= datetime.now().date()]

    st.radio(
        label="Type de jeux",
        options=["olympic", "paralympic"],
        format_func=lambda x: "Olympiques" if x == "olympic" else "Paralympiques",
        key="games_type",
        horizontal=True,
    )

    st.slider(
        label="Distance des événements (km)",
        max_value=20,
        value=5,
        key="events_distance",
    )

    df_sites_filtered = df_sites.loc[
        df_sites["games_type"] == st.session_state["games_type"]
    ]


# ---------- Application : main page

# Get sports list depending on chosen type of games
st.session_state["sports_list"] = generate_sports_list(df_sites_filtered)

st.selectbox(
    label="Sélectionner un sport",
    options=st.session_state["sports_list"],
    key="selected_sport",
)

# Get all available sites information for the selected sport
available_sites = df_sites_filtered.loc[
    df_sites_filtered["sports"].str.contains(
        st.session_state["selected_sport"], regex=False
    )
].to_dict(orient="records")

st.radio(
    label=configure_sites_selection_radio_button(available_sites)[0],
    options=available_sites,
    format_func=lambda x: x["nom_site"],
    key="selected_site",
    captions=configure_sites_selection_radio_button(available_sites)[1],
)


# Get events information
events = get_events_from_site_distance(
    df_events,
    [
        st.session_state["selected_site"]["lat"],
        st.session_state["selected_site"]["lon"],
    ],
    st.session_state["events_distance"],
)

# Initialize Folium map
m = create_folium_map(
    location=[
        st.session_state["selected_site"]["lat"],
        st.session_state["selected_site"]["lon"],
    ]
)

marker_cluster = MarkerCluster().add_to(m)

# Add a marker on the Folium map for the selected site
marker = add_selected_site_marker(site=st.session_state["selected_site"])
marker.add_to(m)

# Add markers on the Folium map for the nearest events
for event in events:
    marker = add_event_marker(event=event)
    marker.add_to(marker_cluster)

# Fit Folium map bounds to selected site and events coordinates
bounds = [[event["latitude"], event["longitude"]] for event in events]
bounds.append([st.session_state["selected_site"]["lat"], st.session_state["selected_site"]["lon"]])
m.fit_bounds(bounds=bounds, padding=(20, 20))

# Render Folium map
st_data = st_folium(m, use_container_width=True)

with st.expander("Events"):
    st.write(events)

with st.expander("Session State"):
    st.write(st.session_state)
