import folium


def create_folium_map(
    location: list = [46.227638, 2.213749], zoom_start: int = 15, max_zoom: int = 20
) -> folium.Map:
    folium_map = folium.Map(
        location=location,
        zoom_start=zoom_start,
        max_zoom=max_zoom,
        zoom_control=False,
        tiles="GeoportailFrance_plan",
        scrollWheelZoom=True,
        dragging=True,
    )
    return folium_map

def add_selected_site_marker(site: dict) -> folium.Marker:
    marker = folium.Marker(
        location=[site["lat"], site["lon"]],
        tooltip=f"{site['nom_site']}",
        popup=f"{site['nom_site']}",
        icon=folium.Icon(icon="glyphicon-flag", color="green", prefix="glyphicon"),
    )
    return marker

def add_event_marker(event: dict) -> folium.Marker:
    marker = folium.Marker(
        location=[event["latitude"], event["longitude"]],
        # tooltip=f"{events['nom_events']}",
        # popup=f"{events['nom_site']}",
        icon=folium.Icon(icon="glyphicon-flag", color="red", prefix="glyphicon"),
    )
    return marker

def create_available_sites_marker(
    site: dict, selected_site_location: list
) -> folium.Marker:
    if not site:
        return folium.Marker(location=[0, 0])

    site_marker = folium.Marker(
        location=[site["lat"], site["lon"]],
        # tooltip=f'Commune : {site["label"]}',
        tooltip="a",
        popup="a",
        icon=folium.Icon(icon="glyphicon-flag", color="green", prefix="glyphicon")
        if set([site["lat"], site["lon"]]) == set(selected_site_location)
        else folium.Icon(icon="glyphicon-flag", color="blue", prefix="glyphicon"),
    )
    return site_marker
