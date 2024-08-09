import json
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils.folium_map import create_folium_map, create_available_sites_marker

# Load competition sites data
with open("datasets/jop2024-competition-sites.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame.from_dict(data, orient="index")

# Convert "start_date" and "end_date" to DateTime format
df[["start_date", "end_date"]] = df[["start_date", "end_date"]].apply(pd.to_datetime)

st.title("JOP2024 et offre culturelle")

st.write("Date et heure actuelle : ", datetime.now().strftime("%d/%m/%Y - %H:%m"))

with st.sidebar:
    st.subheader("Options")
    hide_sites = st.toggle(
        label="Masque les sites selon la date",
        help="Masque les sites où toutes les épreuves prévues se sont déjà déroulées.",
        value=True,
    )
    games_type = st.radio(
        "Type de jeux", ["Olympiques", "Paralympiques"], horizontal=True
    )

if hide_sites:
    df = df.loc[df["end_date"].dt.date >= datetime.now().date()]

if games_type == "Olympiques":
    filtered_df = df.loc[df["games_type"] == "olympic"]
else:
    filtered_df = df.loc[df["games_type"] == "paralympic"]

with st.expander("DataFrame"):
    st.dataframe(filtered_df)

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

with st.expander("Results"):
    st.write(available_sites)

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

st.write(selected_site)

# Initialize Folium map
m = create_folium_map()

# Add a marker on the Folium map for all available site(s)
for site in available_sites:
    site_marker = create_available_sites_marker(
        site=site, selected_site_location=[selected_site["lat"], selected_site["lon"]]
    )
    site_marker.add_to(m)

# Fit Folium map bounds to nearest stations coordinates
m.fit_bounds([[site["lat"], site["lon"]] for site in available_sites])

# Render Folium map
st_data = st_folium(m, width=725)

with st.expander("Session State"):
    st.write(st.session_state)
