import folium.features
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import extra_streamlit_components as stx

from load_data import load_station, load_price, load_data, load_concurrents

st.set_page_config(page_title="Suivi des stations Carrefour", page_icon="📍", layout="wide")

st.markdown("""<style>
    #map_div {
        text-align: center;
    }
    .card_kpi {
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        margin: 10px;
        border: 1px solid #d0d0d0;
        border-radius: 10px;
        box-shadow: 0 0 5px #d0d0d0;
        border-radius: 5px;
    }
    .card_kpi p {
        margin: 0;
        font-size: 20px;
    }
    .card_kpi span {
        font-size: 50px;
        font-weight: bold;
    }
    div.stMainBlockContainer.block-container  {
        padding-top: 50px !important;
    }
    #visualisation-d-une-station {
        padding-top: 0;	
    }
    </style>
        """, 
    unsafe_allow_html=True)

# Chargement des données
df_station = load_station()
df = load_data(df_station=df_station)
concurrents_all_station = load_concurrents(df_station)

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
st.sidebar.markdown("<h2 style='text-align: center;'>Filtres</h2>", unsafe_allow_html=True)

# Sélection de la station Carrefour
station = st.sidebar.selectbox("Station Carrefour", concurrents_all_station.keys())

# Selection des dates
st.sidebar.info(f"Date entre {df['Date'].min().strftime('%Y-%m-%d')} et {df['Date'].max().strftime('%Y-%m-%d')}")
start_date = pd.to_datetime(st.sidebar.date_input("Date de début", df["Date"].min(), min_value=df["Date"].min(), max_value=df["Date"].max()))
end_date = pd.to_datetime(st.sidebar.date_input("Date de fin", df["Date"].max(), min_value=df["Date"].min(), max_value=df["Date"].max()))
df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

# Sélection du rayon
rayon = st.sidebar.select_slider("Sélectionne le rayon en km :", options=range(1,51,1), value=10)
concurrents = {k: v for k, v in concurrents_all_station[station].items() if v <= rayon}
df = df[(df['ID'] == station) | (df["ID"].isin(concurrents.keys()))]
df_station = df_station[(df_station['ID'] == station) | (df_station["ID"].isin(concurrents.keys()))]

### Affichage
## Titre
st.markdown("<h2 style='text-align: center;'>Visualisation d'une station</h2>", unsafe_allow_html=True)

## Calcul informations de la station
def get_df_comparaison(carburant, df):
    # Dataframe avec colonne Enseignes, ID, et Carburant.mean()
    df_carburant = df[df[carburant] > 0].groupby(['ID']).agg({carburant: 'mean'})
    df_carburant = df_carburant.merge(df_station[['ID', 'Enseignes']], on='ID', how='left')
    return df_carburant.sort_values(by=carburant).reset_index(drop=True)

df_carburant_prix_moyen = {}
classements = {}
for carburant in ['Gazole', 'SP95', 'SP98', 'E10', 'E85', 'GPLc']:
    df_carburant_prix_moyen[carburant] = get_df_comparaison(carburant, df)
    classement = df_carburant_prix_moyen[carburant].index[df_carburant_prix_moyen[carburant]['ID'] == station]
    try:
        classements[carburant] = classement[0] + 1
    except:
        pass
classements_global = round(sum(classements.values()) / len(classements), 1)

# Sélection de l'onglet
selected_page = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title="Carte", description="Carte et informations de la station"),
    stx.TabBarItemData(id=2, title="Classement", description="Classement par rapport au concurrent"),
    stx.TabBarItemData(id=3, title="Graphe", description="Evolution du prix"),
], default=1)

## Informations de la station et la carte
if selected_page == "1":
    # Informations de la station
    col_kpi, col_map = st.columns([1, 3])
    col_kpi.markdown(f"""
            <h3>Station {df_station[df_station['ID'] == station]['Enseignes'].values[0]}</h3>
            <h4>Adresse : </h4>
            <h4>{df_station[df_station['ID'] == station]['Adresse'].values[0]}, {df_station[df_station['ID'] == station]['Ville'].values[0]}</h4>
            <hr>
            <div class="card_kpi">
                <p> Nombre de concurrents dans un rayon de {rayon} km</p>
                <span>{len(concurrents)}</span>
            </div>
            <div class="card_kpi">
                <p> Classement globale </p>
                <span>{classements_global} / {len(concurrents)}</span>
            </div>
                """, unsafe_allow_html=True)


    ## Carte
    col_map.markdown("<h3 style='text-align: center;'>Carte des concurrents</h3>", unsafe_allow_html=True)
    map = folium.Map(
        location=[df_station[df_station['ID'] == station]['Latitude'].values[0], df_station[df_station['ID'] == station]['Longitude'].values[0]],
        zoom_start=13
    )

    # Ajout des concurrents
    for concurrent in concurrents.keys():
        folium.Marker(
            location=[df_station[df_station['ID'] == concurrent]['Latitude'].values[0], df_station[df_station['ID'] == concurrent]['Longitude'].values[0]],
            popup=f"<b>{df_station[df_station['ID'] == concurrent]['Enseignes'].values[0]} :</b><br>{df_station[df_station['ID'] == concurrent]['Adresse'].values[0]},{df_station[df_station['ID'] == concurrent]['Ville'].values[0]}",
            icon=folium.Icon(color='red', icon='gas-pump', prefix='fa'),
            tooltip=f"<b>{df_station[df_station['ID'] == concurrent]['Enseignes'].values[0]} :</b><br>{df_station[df_station['ID'] == concurrent]['Adresse'].values[0]},{df_station[df_station['ID'] == concurrent]['Ville'].values[0]}"
        ).add_to(map)

    # Cerle de recherche
    folium.Circle(
        location=[df_station[df_station['ID'] == station]['Latitude'].values[0], df_station[df_station['ID'] == station]['Longitude'].values[0]],
        radius=rayon*1000,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.15
    ).add_to(map)

    # Ajout de la station Carrefour
    folium.Marker(
        location=[df_station[df_station['ID'] == station]['Latitude'].values[0], df_station[df_station['ID'] == station]['Longitude'].values[0]],
        popup=f"<b>{df_station[df_station['ID'] == station]['Enseignes'].values[0]} : </b><br>{df_station[df_station['ID'] == station]['Adresse'].values[0]},{df_station[df_station['ID'] == station]['Ville'].values[0]}",
        icon=folium.features.CustomIcon("./images/carrefour.png", icon_size=(40, 30)),
        tooltip=f"<b>{df_station[df_station['ID'] == station]['Enseignes'].values[0]} : </b><br>{df_station[df_station['ID'] == station]['Adresse'].values[0]},{df_station[df_station['ID'] == station]['Ville'].values[0]}"
    ).add_to(map)

    # Affichage de la carte dans col_map
    with col_map:
        st_folium(map, height=600, use_container_width=True)

## Tableau de comparaison des prix
elif selected_page == "2":
    def highlight_Carrefour(c):
        return ['background-color: green' if c.Enseignes == 'Carrefour' else '' for _ in c]

    col_gazole, col_sp95, col_sp98 = st.columns(3)
    col_gazole.markdown("<h3 style='text-align: center;'>Gazole</h3>", unsafe_allow_html=True)
    if 'Gazole' not in classements.keys():
        col_gazole.warning("Aucune données pour ce carburant.")
    else :
        col_gazole.dataframe(df_carburant_prix_moyen['Gazole'].style.apply(highlight_Carrefour, axis=1), height=250, hide_index=True, use_container_width=True)
    col_sp95.markdown("<h3 style='text-align: center;'>SP95</h3>", unsafe_allow_html=True)
    if 'SP95' not in classements.keys():
        col_sp95.warning("Aucune données pour ce carburant.")
    else :
        col_sp95.dataframe(df_carburant_prix_moyen['SP95'].style.apply(highlight_Carrefour, axis=1), height=250, hide_index=True, use_container_width=True)
    col_sp98.markdown("<h3 style='text-align: center;'>SP98</h3>", unsafe_allow_html=True)
    if 'SP98' not in classements.keys():
        col_sp98.warning("Aucune données pour ce carburant.")
    else :
        col_sp98.dataframe(df_carburant_prix_moyen['SP98'].style.apply(highlight_Carrefour, axis=1), height=250, hide_index=True, use_container_width=True)

    col_e10, col_e85, col_gplc= st.columns(3)
    col_e10.markdown("<h3 style='text-align: center;'>E10</h3>", unsafe_allow_html=True)
    if 'E10' not in classements.keys():
        col_e10.warning("Aucune données pour ce carburant.")
    else :
        col_e10.dataframe(df_carburant_prix_moyen['E10'].style.apply(highlight_Carrefour, axis=1), height=250, hide_index=True, use_container_width=True)
    col_e85.markdown("<h3 style='text-align: center;'>E85</h3>", unsafe_allow_html=True)
    if 'E85' not in classements.keys():
        col_e85.warning("Aucune données pour ce carburant.")
    else :
        col_e85.dataframe(df_carburant_prix_moyen['E85'].style.apply(highlight_Carrefour, axis=1), height=250, hide_index=True, use_container_width=True)
    col_gplc.markdown("<h3 style='text-align: center;'>GPLc</h3>", unsafe_allow_html=True)
    if 'GPLc' not in classements.keys():
        col_gplc.warning("Aucune données pour ce carburant.")
    else :
        col_gplc.dataframe(df_carburant_prix_moyen['GPLc'].style.apply(highlight_Carrefour, axis=1), height=250, hide_index=True, use_container_width=True)

## Graphique de l'évolution des prix 
elif selected_page == "3":
    selected_enseigne = st.multiselect("Sélectionne les enseignes à afficher :", df['Enseignes'].unique(), default=df['Enseignes'].unique())
    def plot_evol_carburant(carburant, df):
        # Création du graphique avec les concurrents
        df_carburant = df[(df[carburant] > 0) & (df["Enseignes"]!='Carrefour')]
        df_carburant = df_carburant[df_carburant['Enseignes'].isin(selected_enseigne)]

        fig = px.line(df_carburant, x='Date', y=carburant, 
                    color="Enseignes",line_group="ID",hover_name='Enseignes',
                    markers=True,
                    color_discrete_sequence=px.colors.sequential.Sunsetdark)
        
        # Ajoute ligne carrefour
        if 'Carrefour' in selected_enseigne:
            df_carburant_carrefour = df[(df[carburant] > 0) & (df["Enseignes"]=='Carrefour')]
            fig.add_scatter(x=df_carburant_carrefour['Date'], 
                            y=df_carburant_carrefour[carburant], 
                            name='Carrefour', 
                            mode='lines+markers',
                            marker={'size': 10, 'color': 'lime', 'symbol':'triangle-up'},
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



