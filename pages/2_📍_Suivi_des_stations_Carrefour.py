import folium.features
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

from load_data import load_station, load_price, load_data, load_concurrents

st.set_page_config(page_title="Suivi des stations Carrefour", page_icon="📍", layout='centered')

st.markdown("""<style>
    #map_div {
        text-align: center; 
    }
    </style>
        """, 
    unsafe_allow_html=True)

# Chargement des données
df_station = load_station()
df = load_data(df_station=df_station)
concurrents = load_concurrents(df_station)

### Sidebar
# Logo
st.sidebar.markdown(
    """
    <div style="text-align: center;">
        <img src="https://my.ecole-hexagone.com/logo-small.svg" width="100">
        <h3>Théo Mourgues M2IA</h3>
        <hr>
    </div>
    """,
    unsafe_allow_html=True
)

# Titre de la sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>Paramètres</h2>", unsafe_allow_html=True)

# Sélection de la station Carrefour
station = st.sidebar.selectbox("Station Carrefour", df_station['ID'].unique())
df = df[(df['ID'] == station) | (df["ID"].isin(concurrents[station].keys()))]
df_station = df_station[(df_station['ID'] == station) | (df_station["ID"].isin(concurrents[station].keys()))]


# Selection des dates
start_date = pd.to_datetime(st.sidebar.date_input("Date de début", df["Date"].min()))
end_date = pd.to_datetime(st.sidebar.date_input("Date de fin", df["Date"].max()))
df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

### Affichage
## Titre
st.markdown("<h1 style='text-align: center;'>Visualisation d'une station</h1>", unsafe_allow_html=True)

## Carte
st.markdown("<h2 style='text-align: center;'>Carte des concurrents</h2><hr>", unsafe_allow_html=True)
map = folium.Map(
    location=[df_station[df_station['ID'] == station]['Latitude'].values[0], df_station[df_station['ID'] == station]['Longitude'].values[0]],
    zoom_start=15
)

# Ajout de la station Carrefour
folium.Marker(
    location=[df_station[df_station['ID'] == station]['Latitude'].values[0], df_station[df_station['ID'] == station]['Longitude'].values[0]],
    popup=f"<b>{df_station[df_station['ID'] == station]['Enseignes'].values[0]} : </b><br>{df_station[df_station['ID'] == station]['Adresse'].values[0]},{df_station[df_station['ID'] == station]['Ville'].values[0]}",
    icon=folium.features.CustomIcon("./images/carrefour.png", icon_size=(40, 30))
).add_to(map)

# Ajout des concurrents
for concurrent in concurrents[station].keys():
    folium.Marker(
        location=[df_station[df_station['ID'] == concurrent]['Latitude'].values[0], df_station[df_station['ID'] == concurrent]['Longitude'].values[0]],
        popup=f"<b>{df_station[df_station['ID'] == concurrent]['Enseignes'].values[0]} :</b><br>{df_station[df_station['ID'] == concurrent]['Adresse'].values[0]},{df_station[df_station['ID'] == concurrent]['Ville'].values[0]}",
        icon=folium.Icon(color='red', icon='gas-pump', prefix='fa')
    ).add_to(map)

# Affichage de la carte
st_folium(map, use_container_width=True)

## Tableau de comparaison des prix
st.markdown("<br><h2 style='text-align: center;'>Tableau de comparaison des prix</h2><hr>", unsafe_allow_html=True)

def highlight_Carrefour(c):
    return ['background-color: green' if c.Enseignes == 'Carrefour' else '' for _ in c]

def get_df_comparaison(carburant, df):
    # Dataframe avec colonne Enseignes, ID, et Carburant.mean()
    df_carburant = df[df[carburant] > 0].groupby(['ID']).agg({carburant: 'mean'})
    df_carburant = df_carburant.merge(df_station[['ID', 'Enseignes']], on='ID', how='left')
    return df_carburant.sort_values(by=carburant)

col_gazole, col_sp95, col_sp98 = st.columns(3)
col_gazole.markdown("<h3 style='text-align: center;'>Gazole</h3>", unsafe_allow_html=True)
col_gazole.dataframe(get_df_comparaison('Gazole', df).style.apply(highlight_Carrefour, axis=1), height=350, hide_index=True)
col_sp95.markdown("<h3 style='text-align: center;'>SP95</h3>", unsafe_allow_html=True)
col_sp95.dataframe(get_df_comparaison('SP95', df).style.apply(highlight_Carrefour, axis=1), height=350, hide_index=True)
col_sp98.markdown("<h3 style='text-align: center;'>SP98</h3>", unsafe_allow_html=True)
col_sp98.dataframe(get_df_comparaison('SP98', df).style.apply(highlight_Carrefour, axis=1), height=350, hide_index=True)

col_e10, col_e85, col_gplc= st.columns(3)
col_e10.markdown("<h3 style='text-align: center;'>E10</h3>", unsafe_allow_html=True)
col_e10.dataframe(get_df_comparaison('E10', df).style.apply(highlight_Carrefour, axis=1), height=350, hide_index=True)
col_e85.markdown("<h3 style='text-align: center;'>E85</h3>", unsafe_allow_html=True)
col_e85.dataframe(get_df_comparaison('E85', df).style.apply(highlight_Carrefour, axis=1), height=350, hide_index=True)
col_gplc.markdown("<h3 style='text-align: center;'>GPLc</h3>", unsafe_allow_html=True)
col_gplc.dataframe(get_df_comparaison('GPLc', df).style.apply(highlight_Carrefour, axis=1), height=350, hide_index=True)

## Graphique de l'évolution des prix 
st.markdown("<br><h2 style='text-align: center;'>Evolution des prix</h2><hr>", unsafe_allow_html=True)

def plot_evol_carburant(carburant, df):
    # Création du graphique avec les concurrents
    df_carburant = df[(df[carburant] > 0) & (df["Enseignes"]!='Carrefour')]

    fig = px.line(df_carburant, x='Date', y=carburant, 
                  color="Enseignes",line_group="ID",hover_name='Enseignes',
                  color_discrete_sequence=px.colors.sequential.Sunsetdark)
    
    # Ajoute ligne carrefour
    df_carburant_carrefour = df[(df[carburant] > 0) & (df["Enseignes"]=='Carrefour')]
    fig.add_scatter(x=df_carburant_carrefour['Date'], 
                    y=df_carburant_carrefour[carburant], 
                    name='Carrefour', 
                    mode='lines', 
                    line=dict(color='green'))
    fig.update_layout(legend_title_text='Enseignes',
                      xaxis_title='Date',
                      yaxis_title='Prix (€)',
                      hovermode='closest',
                      margin=dict(l=0, r=0, t=0, b=10)
                      )

    return fig

col_evo_gazole, col_evo_sp95 = st.columns(2)
col_evo_gazole.markdown("<h3 style='text-align: center;'>Gazole</h3>", unsafe_allow_html=True)
col_evo_gazole.plotly_chart(plot_evol_carburant('Gazole', df), use_container_width=True, config={'displayModeBar': False})
col_evo_sp95.markdown("<h3 style='text-align: center;'>SP95</h3>", unsafe_allow_html=True)
col_evo_sp95.plotly_chart(plot_evol_carburant('SP95', df), use_container_width=True, config={'displayModeBar': False})

col_evo_sp98, col_evo_e10 = st.columns(2)
col_evo_sp98.markdown("<h3 style='text-align: center;'>SP98</h3>", unsafe_allow_html=True)
col_evo_sp98.plotly_chart(plot_evol_carburant('SP98', df), use_container_width=True, config={'displayModeBar': False})
col_evo_e10.markdown("<h3 style='text-align: center;'>E10</h3>", unsafe_allow_html=True)
col_evo_e10.plotly_chart(plot_evol_carburant('E10', df), use_container_width=True, config={'displayModeBar': False})

col_evo_e85, col_evo_gplc = st.columns(2)
col_evo_e85.markdown("<h3 style='text-align: center;'>E85</h3>", unsafe_allow_html=True)
col_evo_e85.plotly_chart(plot_evol_carburant('E85', df), use_container_width=True, config={'displayModeBar': False})
col_evo_gplc.markdown("<h3 style='text-align: center;'>GPLc</h3>", unsafe_allow_html=True)
col_evo_gplc.plotly_chart(plot_evol_carburant('GPLc', df), use_container_width=True, config={'displayModeBar': False})



