import json
from datetime import datetime

import pandas as pd
import streamlit as st

# Load competition sites data
with open("datasets/jop2024-competition-sites.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame.from_dict(data, orient="index")

st.write("Date et heure actuelle : ", datetime.now())

st.title("JOP2024 et offre culturelle")

games_type = st.radio("Type de jeux", ["Olympiques", "Paralympiques"], horizontal=True)

if games_type == "Olympiques":
    filtered_df = df.loc[df["games_type"] == "olympic"]
else:
    filtered_df = df.loc[df["games_type"] == "paralympic"]

st.dataframe(filtered_df)

# Initialize sports list
sports_list = filtered_df["sports"].str.split(",", expand=True)
for col in sports_list.columns:
    sports_list[col] = sports_list[col].str.strip()
sports_list = set(sports_list.stack().sort_values().values)

selected_sport = st.selectbox("Sports", sports_list)

result = filtered_df.loc[filtered_df["sports"].str.contains(selected_sport, regex=False)]

site_name = result["nom_site"].values[0]
start_date = result["start_date"].values[0]
end_date = result["end_date"].values[0]

with st.container(border=True):
    text = f"""
    ### {site_name}  
    Date de début des épreuves : {start_date}  
    Date de fin des épreuves : {end_date}   
    """
    st.markdown(text)