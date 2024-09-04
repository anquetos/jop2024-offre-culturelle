def format_event_display_details(event: tuple) -> str:
    
    md_text = (
f"""    
## {event.name.upper()}
#### Par : {event.nom_structure}
### Description du projet
{event.presentation_projet}
### Informations pratiques
:calendar: Du {event.date_debut.strftime('%d/%m/%Y')} 
à {event.date_debut.strftime('%H:%M')}
au {event.date_fin.strftime('%d/%m/%Y')} 
à {event.date_fin.strftime('%H:%M')}  
:man-woman-girl-boy: {event.public}  
:round_pushpin: {event.lieu_presentation} - {event.addresse}  
:straight_ruler: {round(event.distance_km, 1)} km du site de compétition  
:euro: {event.tarif} : {event.detail_tarif}
"""
    )

    return md_text

def create_event_type_labels(event: tuple) -> str:
    pass

    event_html_list = []

    for event_type in event.discipline_projet.split(","):
        html = f"<span class='label'>{event_type}</span>"

        event_html_list.append(html.strip())

        # Affichage par groupes de 8 mots
        for i in range(0, len( event_html_list), 8):
            event_html = f"<p>{''.join( event_html_list[i:i + 8])}</p>"
    
    return event_html