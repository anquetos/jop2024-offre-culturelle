import folium
import pandas as pd


def create_folium_map(
    location: list = [46.227638, 2.213749], zoom_start: int = 15, max_zoom: int = 18
) -> folium.Map:
    folium_map = folium.Map(
        location=location,
        zoom_start=zoom_start,
        max_zoom=max_zoom,
        zoom_control=True,
        tiles="GeoportailFrance_plan",
        scrollWheelZoom=False,
        dragging=True,
    )
    return folium_map


def add_selected_site_marker(site: dict) -> folium.Marker:
    html = f"""
        Site de compétition<br><b>{site['nom_site']}</b>
        """
    popup = folium.Popup(html)
    tooltip = folium.Tooltip(html)

    marker = folium.Marker(
        location=[site["lat"], site["lon"]],
        tooltip=tooltip,
        popup=popup,
        icon=folium.Icon(color="green", icon="house-flag", prefix="fa"),
    )

    return marker


def add_event_location_marker(
    events: pd.DataFrame, location: list[float, float]
) -> folium.Marker:
    # Filter events by their location
    df = events.loc[
        (events["latitude"] == location[0]) & (events["longitude"] == location[1])
    ]
    # Initialize a list which will contain an html code for each event
    event_html_list = []
    # Iterate over events
    for i, row in enumerate(df.itertuples(), 1):
        # Generate html
        html = f"""
            <b>{i}. {row.name}</b><br>
            {row.lieu_presentation} (<i>{round(row.distance_km, 1)} km</i>)<br>
            Du <b>{row.date_debut.strftime('%d/%m/%Y')}</b> 
            à <b>{row.date_debut.strftime('%H:%M')}</b>
            au <b>{row.date_fin.strftime('%d/%m/%Y')}</b>
            à <b>{row.date_fin.strftime('%H:%M')}</b><br>
            """
        # Add html to the list
        event_html_list.append(html.strip())

    # Concatenate the html list to one html
    event_html = "<br>".join(event_html_list)

    # Create markers
    popup = folium.Popup(event_html, max_width=200)
    tooltip = folium.Tooltip(event_html)
    markers = folium.Marker(
        location=location,
        popup=popup,
        tooltip=tooltip,
        icon=folium.Icon(color="blue", icon="circle-info", prefix="fa"),
    )

    return markers
