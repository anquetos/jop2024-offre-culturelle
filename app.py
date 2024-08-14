import json
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils.folium_map import create_folium_map, add_selected_site_marker


# Defaut setting of the app page
st.set_page_config(
    page_title="JO Paris 2024 · Explorer",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load competition sites data
@st.cache_data
def load_competition_sites() -> pd.DataFrame:
    with open("datasets/jop2024-competition-sites.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index")
    return df


df_competition_sites = load_competition_sites()

# Convert "start_date" and "end_date" to DateTime format
df_competition_sites[["start_date", "end_date"]] = df_competition_sites[
    ["start_date", "end_date"]
].apply(pd.to_datetime)

st.title("JOP2024 et offre culturelle")

# st.write("Date et heure actuelle : ", datetime.now().strftime("%d/%m/%Y - %H:%m"))

with st.sidebar:
    st.subheader("Options")
    hide_sites = st.toggle(
        label="Masque les sites selon la date",
        help="Masque les sites où toutes les épreuves prévues se sont déjà déroulées.",
        value=False,
    )
    games_type = st.radio(
        "Type de jeux", ["Olympiques", "Paralympiques"], horizontal=True
    )

if hide_sites:
    df_competition_sites = df_competition_sites.loc[
        df_competition_sites["end_date"].dt.date >= datetime.now().date()
    ]

if games_type == "Olympiques":
    filtered_df = df_competition_sites.loc[
        df_competition_sites["games_type"] == "olympic"
    ]
else:
    filtered_df = df_competition_sites.loc[
        df_competition_sites["games_type"] == "paralympic"
    ]

# with st.expander("DataFrame"):
#     st.dataframe(filtered_df)

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

# st.write(selected_site)

# Initialize Folium map
m = create_folium_map(location=[selected_site["lat"], selected_site["lon"]])

# Add a marker on the Folium map for the selected site
marker = add_selected_site_marker(site=selected_site)
marker.add_to(m)

# Fit Folium map bounds to nearest stations coordinates
# m.fit_bounds([[site["lat"], site["lon"]] for site in available_sites])

# Render Folium map
st_data = st_folium(m, use_container_width=True)

with st.expander("Session State"):
    st.write(st.session_state)
