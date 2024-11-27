import streamlit as st
import pandas as pd
from tqdm import tqdm
import time

from load_data import *

st.set_page_config(page_title="Suivi des stations Carrefour", page_icon="📍", layout='centered')

# Chargement des données
df_station = load_station()
df_price = load_price()
df = load_data(df_station, df_price)
concurrents = load_concurrents()
# Séparer Carrefour avec toutes les enseignes
df_carrefour = df[df['Enseignes'] == 'Carrefour']
df = df[df['Enseignes'] != 'Carrefour']


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
station = st.sidebar.selectbox("Station Carrefour", df_carrefour['ID'].unique())

# Selection des dates
start_date = pd.to_datetime(st.sidebar.date_input("Date de début", df["Date"].min()))
end_date = pd.to_datetime(st.sidebar.date_input("Date de fin", df["Date"].max()))
df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

