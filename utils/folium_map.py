import folium


def create_folium_map(zoom_start: int = 5) -> folium.Map:
    folium_map = folium.Map(
        location=[46.227638, 2.213749],
        zoom_start=zoom_start,
        zoom_control=True,
        tiles="GeoportailFrance_plan",
        scrollWheelZoom=False,
        dragging=True,
    )
    return folium_map


def create_selected_city_marker(city: dict) -> folium.Marker:
    if not city:
        return folium.Marker(location=[0, 0])

    city_marker = folium.Marker(
        location=[city["lat"], city["lon"]],
        tooltip=f'Commune : {city["label"]}',
        icon=folium.Icon(icon="glyphicon-home", color="darkred", prefix="glyphicon"),
    )
    return city_marker


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
