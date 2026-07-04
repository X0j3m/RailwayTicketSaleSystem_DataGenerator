# AI GENERATED

import os
import urllib.request
import socket
import geopandas as gpd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context

from json_handler import open_json_file, save_json_file
from models import StationModel, ConnectionModel
from connections_data_filler import fill_connections_data
from map_generator import generate_map

RES_PATH = "../res"
LOCAL_GEOJSON_PATH = os.path.join(RES_PATH, "../res/wojewodztwa-min.geojson")
URL = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-max.geojson"
generate_map()

def load_data():
    os.makedirs(RES_PATH, exist_ok=True)
    if not os.path.exists(LOCAL_GEOJSON_PATH):
        try:
            socket.setdefaulttimeout(10)
            urllib.request.urlretrieve(URL, LOCAL_GEOJSON_PATH)
        except Exception as e:
            return None, [], []

    stations_dict = open_json_file("train_stations")
    stations = [StationModel(**item) for item in stations_dict]

    try:
        connections_dict = open_json_file("train_stations_connections")
        connections = [ConnectionModel(**item) for item in connections_dict]
    except Exception:
        connections = []

    poland_provinces = gpd.read_file(LOCAL_GEOJSON_PATH)

    poland_provinces = poland_provinces.to_crs(epsg=4326)

    return poland_provinces, stations, connections


poland_provinces, stations, connections = load_data()

stations_by_id = {str(s.id): s for s in stations}

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Interaktywny Kreator Połączeń Kolejowych", style={'textAlign': 'center', 'fontFamily': 'Arial'}),

    html.Div([
        html.Button("Wyczyść zaznaczenie", id="clear-btn", n_clicks=0,
                    style={'marginRight': '10px', 'padding': '10px'}),
        html.Button("Zapisz połączenia do JSON", id="save-btn", n_clicks=0,
                    style={'backgroundColor': '#119448', 'color': 'white', 'padding': '10px'}),
        html.Div(id="status-output", style={'marginTop': '10px', 'fontWeight': 'bold', 'color': '#555'})
    ], style={'marginBottom': '20px', 'textAlign': 'center'}),

    # Przechowywanie stanu aplikacji w pamięci przeglądarki
    dcc.Store(id='selected-stations', data=[]),  # Przechowuje aktualnie kliknięte stacje (max 2)
    dcc.Store(id='live-connections', data=[c.model_dump() for c in connections]),  # Przechowuje listę połączeń

    # Wykres interaktywny
    dcc.Graph(id='poland-map', style={'height': '80vh'})
])


def create_figure(stations_list, connections_list, selected_ids):
    fig = go.Figure()

    # 1. Rysowanie granic województw
    for _, row in poland_provinces.iterrows():
        if row['geometry'].geom_type == 'Polygon':
            x, y = row['geometry'].exterior.xy
            fig.add_trace(go.Scatter(x=list(x), y=list(y), mode='lines',
                                     line=dict(color='#8a8a8a', width=0.5),
                                     hoverinfo='skip', showlegend=False))
        elif row['geometry'].geom_type == 'MultiPolygon':
            for poly in row['geometry'].geoms:
                x, y = poly.exterior.xy
                fig.add_trace(go.Scatter(x=list(x), y=list(y), mode='lines',
                                         line=dict(color='#8a8a8a', width=0.5),
                                         hoverinfo='skip', showlegend=False))

    for conn in connections_list:
        src = stations_by_id.get(str(conn['source_id']))
        tgt = stations_by_id.get(str(conn['target_id']))
        if src and tgt:
            fig.add_trace(go.Scatter(
                x=[src.longitude, tgt.longitude],
                y=[src.latitude, tgt.latitude],
                mode='lines',
                line=dict(color='red', width=1.5),
                hoverinfo='skip',
                showlegend=False
            ))

    lon_s, lat_s, names_s, ids_s, colors_s, sizes_s = [], [], [], [], [], []
    for s in stations_list:
        lon_s.append(s.longitude)
        lat_s.append(s.latitude)
        names_s.append(s.city)
        ids_s.append(str(s.id))

        if str(s.id) in selected_ids:
            colors_s.append('#119448')
            sizes_s.append(14)
        else:
            colors_s.append('#1200bb')
            sizes_s.append(8)

    fig.add_trace(go.Scatter(
        x=lon_s, y=lat_s, mode='markers+text',
        marker=dict(color=colors_s, size=sizes_s),
        text=names_s, textposition="top center",
        textfont=dict(size=9, color='black'),
        customdata=ids_s,  # Przekazanie ID do obsługi kliknięć
        name="Stacje",
        hoverinfo='text'
    ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        showlegend=False
    )
    return fig


@app.callback(
    [Output('poland-map', 'figure'),
     Output('selected-stations', 'data'),
     Output('live-connections', 'data'),
     Output('status-output', 'children')],
    [Input('poland-map', 'clickData'),
     Input('clear-btn', 'n_clicks'),
     Input('save-btn', 'n_clicks')],
    [State('selected-stations', 'data'),
     State('live-connections', 'data')]
)
def handle_interaction(click_data, clear_clicks, save_clicks, selected_ids, current_connections):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    status_msg = "Kliknij dwie stacje, aby utworzyć między nimi połączenie."

    if triggered_id == 'clear-btn':
        selected_ids = []
        status_msg = "Wyczyszczono zaznaczenie stacji."

    elif triggered_id == 'save-btn':
        fill_connections_data()
        save_json_file("train_stations_connections", current_connections)
        status_msg = f"Sukces! Zapisano {len(current_connections)} połączeń do pliku JSON."
        selected_ids = []

    elif triggered_id == 'poland-map' and click_data:
        try:
            clicked_station_id = click_data['points'][0]['customdata']

            if clicked_station_id in selected_ids:
                selected_ids.remove(clicked_station_id)
                status_msg = "Odznaczono stację."
            else:
                selected_ids.append(clicked_station_id)
                status_msg = f"Zaznaczono stację. (Wybranych: {len(selected_ids)}/2)"

            if len(selected_ids) == 2:
                src_id, tgt_id = selected_ids[0], selected_ids[1]

                exists = any(
                    (c['source_id'] == src_id and c['target_id'] == tgt_id) or
                    (c['source_id'] == tgt_id and c['target_id'] == src_id)
                    for c in current_connections
                )

                if not exists:
                    new_conn = {
                        "source_id": src_id,
                        "target_id": tgt_id,
                        "num_id": len(current_connections) + 1
                    }
                    current_connections.append(new_conn)
                    status_msg = f"Dodano nowe połączenie pomiędzy {stations_by_id[src_id].city} a {stations_by_id[tgt_id].city}!"
                else:
                    status_msg = "To połączenie już istnieje!"

                selected_ids = []

        except KeyError:
            pass

    fig = create_figure(stations, current_connections, selected_ids)
    return fig, selected_ids, current_connections, status_msg


if __name__ == "__main__":
    app.run(debug=True, port=8050)
