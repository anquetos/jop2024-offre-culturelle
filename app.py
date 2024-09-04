import json

import pandas as pd
import streamlit as st
from geopy import distance
from streamlit_folium import st_folium

from utils.folium_map import (
    add_event_location_marker,
    add_selected_site_marker,
    create_folium_map,
)
from utils.utils import create_event_type_labels, format_event_display_details

# ---------- Page configuration
st.set_page_config(
    page_title="JO Paris 2024 · Explorer",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Functions


@st.cache_data
def load_competition_sites() -> pd.DataFrame:
    """Load competition sites data.

    Returns:
        pd.DataFrame: competition sites dataset.
    """
    with open("datasets/jop2024-competition-sites.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index")
    df[["start_date", "end_date"]] = df[["start_date", "end_date"]].apply(
        pd.to_datetime
    )
    return df


@st.cache_data
def load_events() -> pd.DataFrame:
    """Load cultural events data.

    Returns:
        pd.DataFrame: cultural events dataset.
    """
    with open("datasets/jop2024-evenements.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index")
    df[["date_debut", "date_fin"]] = df[["date_debut", "date_fin"]].apply(
        pd.to_datetime
    )

    return df


@st.cache_data
def generate_sports_list(df: pd.DataFrame) -> list[str]:
    """List all sports.

    Args:
        df (pd.DataFrame): competition datasets.

    Returns:
        list[str]: A list of all the sports.
    """
    sports_list = df["sports"].str.split(", ").explode()
    sports_list = sorted(list(set(sports_list)))

    return sports_list


@st.cache_data
def get_available_sites_for_selected_sport(sites: pd.DataFrame, sport: str) -> dict:
    """Find sites and their information  where there will be competitions for a specific
    sport.

    Args:
        sites (pd.DataFrame): competition dataset.
        sport (str): sport.

    Returns:
        dict: sites informations in a dictionnary.
    """
    available_sites = sites.loc[
        sites["sports"].str.contains(sport, regex=False)
    ].to_dict(orient="records")

    return available_sites


@st.cache_data
def get_events_types_list(df: pd.DataFrame) -> list[str]:
    """List events types.

    Args:
        df (pd.DataFrame): cultural events dataset.

    Returns:
        list[str]: A list of all events types.
    """
    events_type_list = df["discipline_projet"].str.split(", ").explode()
    events_type_list = sorted(list(set(events_type_list)))

    return events_type_list


@st.cache_data
def configure_sites_selection_radio_button(sites: dict) -> tuple[str, list]:
    """Create 'labels' and 'captions' for the st.radio() widget to select a competition
    site.

    Args:
        sites (dict): dictionnay of sites informations

    Returns:
        tuple[str, list]: the label of the radio widget and its captions texts.s
    """
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


@st.cache_data
def get_events_by_distance(
    events: pd.DataFrame, site_location: list[float], events_distance: float
) -> pd.DataFrame:
    """Compute the distance between a competition site and events and filter them
    depending on their distance.

    Args:
        events (pd.DataFrame): events datasets.
        site_location (list[float]): coordinates of a competition site.
        events_distance (float): maximum distance of events in kilometers.

    Returns:
        pd.DataFrame: filtered events datasets based on the competition site distance.
    """
    events = events.copy()
    events["distance_km"] = events.apply(
        lambda x: distance.distance([x["latitude"], x["longitude"]], site_location).km,
        axis="columns",
    )
    events = events.sort_values(by=["distance_km"])
    events = events.loc[events["distance_km"] <= events_distance]

    return events


@st.cache_data
def get_events_by_types(events: pd.DataFrame, events_types: list[str]) -> pd.DataFrame:
    """Filter events depending on specific types.

    Args:
        events (pd.DataFrame): events datasets.
        events_types (list[str]): events types.

    Returns:
        pd.DataFrame: filtered events dataset based on their types.
    """
    events = events.copy()
    events = events.loc[
        events["discipline_projet"].str.contains("|".join(events_types))
    ]

    return events


@st.cache_data
def get_events_location_data(
    events: pd.DataFrame,
) -> tuple[int, list[float, float], int]:
    """Compute information about events and their locations.

    Args:
        events (pd.DataFrame): events dataset.

    Returns:
        tuple[int, list[float, float], int]: number of events, list of coordinates and
        number of unique locations of events.
    """
    n_events = len(events)
    locations_list = (
        events[["latitude", "longitude"]]
        .drop_duplicates(subset=["latitude", "longitude"])
        .values.tolist()
    )
    n_locations = len(locations_list)

    return n_events, locations_list, n_locations


@st.cache_data
def get_specific_location_events(events: pd.DataFrame, location: dict) -> pd.DataFrame:
    """Get all events for a specific location.

    Args:
        events (pd.DataFrame): events dataset.
        location (dict): specific coordinates.

    Returns:
        pd.DataFrame: filtered events dataset for a specific location.
    """
    df = events.loc[
        (events["latitude"] == location["lat"])
        & (events["longitude"] == location["lng"])
    ]

    return df


# ---------- Initialize Session State values

# ---------- Get and cache data
df_sites = load_competition_sites()
df_events = load_events()

#################
# Streamlit app #
#################

st.title("JO Paris 2024 · Explorer")
st.markdown("#### Explorez l'offre culturelle autour des sites de compétition")

# ---------- Application : sidebar

with st.sidebar:
    st.image("./assets/images/logo-paris-2024.png")

    st.header("Paramètres")

    st.radio(
        label="Type de jeux",
        options=["olympic", "paralympic"],
        format_func=lambda x: "Olympiques" if x == "olympic" else "Paralympiques",
        key="games_type",
        horizontal=True,
    )

    st.subheader("Evénements", divider="grey")

    st.slider(
        label="Distance maximale",
        max_value=20,
        value=5,
        key="events_max_distance",
        help="Distance en kilomètres depuis le site de compétition sélectionné",
    )

    st.multiselect(
        label="Filtrer par type",
        options=get_events_types_list(df_events),
        key="selected_events_types",
        placeholder="Choisissez une ou plusieurs option(s)",
    )

    st.subheader("A propos", divider="grey")

    st.markdown("""
        L' application ***JO Paris 2024 · Explorer*** permet de trouver les **sites de 
        compétitions** où se déroulent les épreuves d'un **sport** en  particulier puis 
        d\'afficher et filtrer les **événements culturelles** à proximité.
    """)

    st.caption("""
        Auteur : T. Anquetil ([GitHub](https://github.com/anquetos) & 
        [LinkedIn](https://www.linkedin.com/in/thomas-anquetil-132a73123)) 
        · Août 2024
    """)

# ---------- Application : main page => selection

# Filter sites data depending on games type
df_sites_games_type_filtered = df_sites.loc[
    df_sites["games_type"] == st.session_state["games_type"]
]

with st.popover(
    label="**Choisissez un sport et un site de compétition**",
    use_container_width=True,
):
    st.selectbox(
        label="Sélectionner un sport",
        options=generate_sports_list(df_sites_games_type_filtered),
        key="selected_sport",
    )

    # Get competition sites information for the selected sport
    available_sites = get_available_sites_for_selected_sport(
        df_sites_games_type_filtered, st.session_state["selected_sport"]
    )

    st.radio(
        label=configure_sites_selection_radio_button(available_sites)[0],
        options=available_sites,
        format_func=lambda x: x["nom_site"],
        key="selected_site",
        captions=configure_sites_selection_radio_button(available_sites)[1],
    )

# Filter events depending on their distance from the selected competition site
df_events_by_distance = get_events_by_distance(
    df_events,
    [
        st.session_state["selected_site"]["lat"],
        st.session_state["selected_site"]["lon"],
    ],
    st.session_state["events_max_distance"],
)

# Filter events depending on their type
df_events_by_distance_and_type = get_events_by_types(
    df_events_by_distance, st.session_state["selected_events_types"]
)

# Get events unique location and counts
n_events, events_locations_list, n_events_locations = get_events_location_data(
    df_events_by_distance_and_type
)

st.info(f"""
    :mag: Il y a **{n_events}** événement(s) dans **{n_events_locations}** lieu(x) 
    différent(s).  
    :world_map: **Survolez** le(s) marqueur(s) sur la carte pour avoir un **aperçu** ou 
    **cliquez** dessus pour obtenir des **informations détaillées**.
""")

# ---------- Application : main page => display map

# Initialize Folium map
map = create_folium_map(
    location=[
        st.session_state["selected_site"]["lat"],
        st.session_state["selected_site"]["lon"],
    ]
)

# Add a marker on the map for the selected site
add_selected_site_marker(site=st.session_state["selected_site"]).add_to(map)

# Add markers on the map for the nearest events unique* location
# * Several events can take place in the same location but we don't want to
# duplicate the same marker.
for location in events_locations_list:
    add_event_location_marker(df_events_by_distance_and_type, location).add_to(map)

# Fit Folium map bounds to selected site and events coordinates
bounds = events_locations_list
bounds.append(
    [st.session_state["selected_site"]["lat"], st.session_state["selected_site"]["lon"]]
)
map.fit_bounds(bounds=bounds, padding=(20, 20))

# Render Folium map
st_data = st_folium(map, use_container_width=True)

# ---------- Application : main page => display detailed information

# Display detailed information of events in the selected location
if st_data["last_object_clicked"]:
    events_of_location = get_specific_location_events(
        df_events_by_distance_and_type, st_data["last_object_clicked"]
    )

    st.subheader("Détails des événements")

    st.info(
        f":ticket: **{len(events_of_location)}** évenement(s) culturel(s) prévu(s) dans ce lieu."
    )

    # Generate one tab for each different event of a specific location
    tabs = st.tabs([f"Evénement {str(i+1)}" for i in range(len(events_of_location))])

    for i, row in enumerate(events_of_location.itertuples()):
        with tabs[i]:
            body = format_event_display_details(row)
            st.markdown(body)

            st.markdown("**Type d'événement(s) :**")

            st.markdown(create_event_type_labels(row), unsafe_allow_html=True)

            # CSS style for event type labels
            st.markdown(
                """
                <style>
                .label {
                    background: #9F862D;
                    border-radius: 6px;
                    margin: 4px;
                    padding: 6px 8px;
                    display: inline-block;
                    color: white;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
