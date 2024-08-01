import json
from datetime import datetime

import pandas as pd
import streamlit as st

# Load competition sites data
with open("datasets/paris-2024-sites-de-competition.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.json_normalize(data)

st.write("Date et heure actuelle : ", datetime.now())

st.title("JOP2024 et offre culturelle")

games_type = st.radio("Type de jeux", ["Olympiques", "Paralympiques"], horizontal=True)

if games_type == "Olympiques":
    filtered_df = df.loc[df["category_id"] == "venue-olympic"]
else:
    filtered_df = df.loc[df["category_id"] == "venue-paralympic"]

st.dataframe(filtered_df)

# Initialize sports list
sports_list = filtered_df["sports"].str.split(",", expand=True)
for col in sports_list.columns:
    sports_list[col] = sports_list[col].str.strip()
sports_list = set(sports_list.stack().values)

selected_sport = st.selectbox("Sports", sports_list)

result = filtered_df.loc[filtered_df["sports"].str.contains(selected_sport, regex=False)]

site_name = result["nom_site"].values[0]

st.write(site_name)