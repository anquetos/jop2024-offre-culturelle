import folium


def create_folium_map(
    location: list = [46.227638, 2.213749], zoom_start: int = 5, max_zoom: int = 15
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


def create_selected_site_marker(site: dict) -> folium.Marker:
    if not site:
        return folium.Marker(location=[0, 0])

    site_marker = folium.Marker(
        location=[site["lat"], site["lon"]],
        # tooltip=f'Commune : {site["label"]}',
        tooltip="a",
        popup="a",
        icon=folium.Icon(icon="glyphicon-flag", color="darkred", prefix="glyphicon"),
    )
    return site_marker


def create_stations_markers(index: int, station: dict) -> folium.Marker:
    if not station:
        return folium.Marker(location=[0, 0])

    stations_markers = folium.Marker(
        location=[station["latitude"], station["longitude"]],
        tooltip=f'Station : {station["nom_usuel"]}',
        icon=folium.Icon(icon="glyphicon-star", color="green", prefix="glyphicon")
        if index == 0
        else folium.Icon(icon="glyphicon-map-marker", color="blue", prefix="glyphicon"),
    )
    return stations_markers
