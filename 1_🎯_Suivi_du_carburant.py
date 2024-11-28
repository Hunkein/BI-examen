import streamlit as st
import pandas as pd
from load_data import *
 

st.set_page_config(page_title="Suivi du carburant", page_icon="🎯", layout="wide")

# Chargement du style css

st.markdown("""<style>
    .stColumn {
        padding: 5px;
        border: 1px solid #d0d0d0;
        border-radius: 10px;
        box-shadow: 0 0 5px #d0d0d0;
        text-align: center; 
        min-width: 200px;
    }
    .stColumn p {
        margin: 0;
        font-size: 20px;
    }
    .stColumn .stMarkdown p {
        margin: 0;
        font-size: 30px;
        font-weight: bold;
        height: 60px;
    }
    .stColumn svg {
        display: none;
    }

    </style>
        """, 
    unsafe_allow_html=True)


# Chargement des données
df = load_data()


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
# Selection des dates
start_date = pd.to_datetime(st.sidebar.date_input("Date de début", df["Date"].min()))
end_date = pd.to_datetime(st.sidebar.date_input("Date de fin", df["Date"].max()))
df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]


## Affichage des KPIs

# Titre
st.markdown("<h1 style='text-align: center;'>KPIs</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Prix moyen en euros</h2>", unsafe_allow_html=True)

def get_rank_delta_color(sort_kpis, price):
    index = sort_kpis.index(price)
    if index == 0:
        delta_color = "normal"
    elif index == 5:
        delta_color = "inverse"
    else:
        delta_color = "off"
    return index+1, delta_color

def get_kpis():
    kpis = {
        "Carrefour": {},
        "Auchan": {},
        "Leclerc": {},
        "Total Access": {},
        "Intermarche": {},
        "Super U": {}
    }
    for carburant in ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]:
        price_carrefour = df[(df["Enseignes"] == "Carrefour") & (df[carburant] != 0)][carburant].mean().round(2)
        price_auchan = df[(df["Enseignes"] == "Auchan") & (df[carburant] != 0)][carburant].mean().round(2)
        price_leclerc = df[(df["Enseignes"] == "E.Leclerc") & (df[carburant] != 0)][carburant].mean().round(2)
        price_total_access = df[(df["Enseignes"] == "Total Access") & (df[carburant] != 0)][carburant].mean().round(2)
        price_intermarche = df[(df["Enseignes"] == "Intermarche") & (df[carburant] != 0)][carburant].mean().round(2)
        price_super_u = df[(df["Enseignes"] == "Super U") & (df[carburant] != 0)][carburant].mean().round(2)

        sort_kpis = sorted([price_carrefour, price_auchan, price_leclerc, price_total_access, price_intermarche, price_super_u])
        
        index, delta_color = get_rank_delta_color(sort_kpis, price_carrefour)
        kpis["Carrefour"][carburant] = {"Prix moyen": price_carrefour, "Classement": f"rang : {index}", "delta_color":delta_color}
        index, delta_color = get_rank_delta_color(sort_kpis, price_auchan)
        kpis["Auchan"][carburant] = {"Prix moyen": price_auchan, "Classement": f"rang : {index}", "delta_color":delta_color}
        index, delta_color = get_rank_delta_color(sort_kpis, price_leclerc)
        kpis["Leclerc"][carburant] = {"Prix moyen": price_leclerc, "Classement": f"rang : {index}", "delta_color":delta_color}
        index, delta_color = get_rank_delta_color(sort_kpis, price_total_access)
        kpis["Total Access"][carburant] = {"Prix moyen": price_total_access, "Classement": f"rang : {index}", "delta_color":delta_color}
        index, delta_color = get_rank_delta_color(sort_kpis, price_intermarche)
        kpis["Intermarche"][carburant] = {"Prix moyen": price_intermarche, "Classement": f"rang : {index}", "delta_color":delta_color}
        index, delta_color = get_rank_delta_color(sort_kpis, price_super_u)
        kpis["Super U"][carburant] = {"Prix moyen": price_super_u, "Classement": f"rang : {index}", "delta_color":delta_color}

    return kpis

kpis = get_kpis()    

col_carrefour, col_auchan, col_leclerc, col_total_access, col_intermarche, col_super_u = st.columns(6)

col_carrefour.write("Carrefour")
col_carrefour.metric("Gazole", kpis["Carrefour"]["Gazole"]["Prix moyen"], delta=kpis["Carrefour"]["Gazole"]["Classement"], delta_color=kpis["Carrefour"]["Gazole"]["delta_color"])
col_carrefour.metric("SP95", kpis["Carrefour"]["SP95"]["Prix moyen"], delta=kpis["Carrefour"]["SP95"]["Classement"], delta_color=kpis["Carrefour"]["SP95"]["delta_color"])
col_carrefour.metric("SP98", kpis["Carrefour"]["SP98"]["Prix moyen"], delta=kpis["Carrefour"]["SP98"]["Classement"], delta_color=kpis["Carrefour"]["SP98"]["delta_color"])
col_carrefour.metric("E10", kpis["Carrefour"]["E10"]["Prix moyen"], delta=kpis["Carrefour"]["E10"]["Classement"], delta_color=kpis["Carrefour"]["E10"]["delta_color"])
col_carrefour.metric("E85", kpis["Carrefour"]["E85"]["Prix moyen"], delta=kpis["Carrefour"]["E85"]["Classement"], delta_color=kpis["Carrefour"]["E85"]["delta_color"])
col_carrefour.metric("GPLc", kpis["Carrefour"]["GPLc"]["Prix moyen"], delta=kpis["Carrefour"]["GPLc"]["Classement"], delta_color=kpis["Carrefour"]["GPLc"]["delta_color"])

col_auchan.write("Auchan")
col_auchan.metric("Gazole", kpis["Auchan"]["Gazole"]["Prix moyen"], delta=kpis["Auchan"]["Gazole"]["Classement"], delta_color=kpis["Auchan"]["Gazole"]["delta_color"])
col_auchan.metric("SP95", kpis["Auchan"]["SP95"]["Prix moyen"], delta=kpis["Auchan"]["SP95"]["Classement"], delta_color=kpis["Auchan"]["SP95"]["delta_color"])
col_auchan.metric("SP98", kpis["Auchan"]["SP98"]["Prix moyen"], delta=kpis["Auchan"]["SP98"]["Classement"], delta_color=kpis["Auchan"]["SP98"]["delta_color"])
col_auchan.metric("E10", kpis["Auchan"]["E10"]["Prix moyen"], delta=kpis["Auchan"]["E10"]["Classement"], delta_color=kpis["Auchan"]["E10"]["delta_color"])
col_auchan.metric("E85", kpis["Auchan"]["E85"]["Prix moyen"], delta=kpis["Auchan"]["E85"]["Classement"], delta_color=kpis["Auchan"]["E85"]["delta_color"])
col_auchan.metric("GPLc", kpis["Auchan"]["GPLc"]["Prix moyen"], delta=kpis["Auchan"]["GPLc"]["Classement"], delta_color=kpis["Auchan"]["GPLc"]["delta_color"])

col_leclerc.write("Leclerc")
col_leclerc.metric("Gazole", kpis["Leclerc"]["Gazole"]["Prix moyen"], delta=kpis["Leclerc"]["Gazole"]["Classement"], delta_color=kpis["Leclerc"]["Gazole"]["delta_color"])
col_leclerc.metric("SP95", kpis["Leclerc"]["SP95"]["Prix moyen"], delta=kpis["Leclerc"]["SP95"]["Classement"], delta_color=kpis["Leclerc"]["SP95"]["delta_color"])
col_leclerc.metric("SP98", kpis["Leclerc"]["SP98"]["Prix moyen"], delta=kpis["Leclerc"]["SP98"]["Classement"], delta_color=kpis["Leclerc"]["SP98"]["delta_color"])
col_leclerc.metric("E10", kpis["Leclerc"]["E10"]["Prix moyen"], delta=kpis["Leclerc"]["E10"]["Classement"], delta_color=kpis["Leclerc"]["E10"]["delta_color"])
col_leclerc.metric("E85", kpis["Leclerc"]["E85"]["Prix moyen"], delta=kpis["Leclerc"]["E85"]["Classement"], delta_color=kpis["Leclerc"]["E85"]["delta_color"])
col_leclerc.metric("GPLc", kpis["Leclerc"]["GPLc"]["Prix moyen"], delta=kpis["Leclerc"]["GPLc"]["Classement"], delta_color=kpis["Leclerc"]["GPLc"]["delta_color"])

col_total_access.write("Total Access")
col_total_access.metric("Gazole", kpis["Total Access"]["Gazole"]["Prix moyen"], delta=kpis["Total Access"]["Gazole"]["Classement"], delta_color=kpis["Total Access"]["Gazole"]["delta_color"])
col_total_access.metric("SP95", kpis["Total Access"]["SP95"]["Prix moyen"], delta=kpis["Total Access"]["SP95"]["Classement"], delta_color=kpis["Total Access"]["SP95"]["delta_color"])
col_total_access.metric("SP98", kpis["Total Access"]["SP98"]["Prix moyen"], delta=kpis["Total Access"]["SP98"]["Classement"], delta_color=kpis["Total Access"]["SP98"]["delta_color"])
col_total_access.metric("E10", kpis["Total Access"]["E10"]["Prix moyen"], delta=kpis["Total Access"]["E10"]["Classement"], delta_color=kpis["Total Access"]["E10"]["delta_color"])
col_total_access.metric("E85", kpis["Total Access"]["E85"]["Prix moyen"], delta=kpis["Total Access"]["E85"]["Classement"], delta_color=kpis["Total Access"]["E85"]["delta_color"])
col_total_access.metric("GPLc", kpis["Total Access"]["GPLc"]["Prix moyen"], delta=kpis["Total Access"]["GPLc"]["Classement"], delta_color=kpis["Total Access"]["GPLc"]["delta_color"])

col_intermarche.write("Inter")
col_intermarche.metric("Gazole", kpis["Intermarche"]["Gazole"]["Prix moyen"], delta=kpis["Intermarche"]["Gazole"]["Classement"], delta_color=kpis["Intermarche"]["Gazole"]["delta_color"])
col_intermarche.metric("SP95", kpis["Intermarche"]["SP95"]["Prix moyen"], delta=kpis["Intermarche"]["SP95"]["Classement"], delta_color=kpis["Intermarche"]["SP95"]["delta_color"])
col_intermarche.metric("SP98", kpis["Intermarche"]["SP98"]["Prix moyen"], delta=kpis["Intermarche"]["SP98"]["Classement"], delta_color=kpis["Intermarche"]["SP98"]["delta_color"])
col_intermarche.metric("E10", kpis["Intermarche"]["E10"]["Prix moyen"], delta=kpis["Intermarche"]["E10"]["Classement"], delta_color=kpis["Intermarche"]["E10"]["delta_color"])
col_intermarche.metric("E85", kpis["Intermarche"]["E85"]["Prix moyen"], delta=kpis["Intermarche"]["E85"]["Classement"], delta_color=kpis["Intermarche"]["E85"]["delta_color"])
col_intermarche.metric("GPLc", kpis["Intermarche"]["GPLc"]["Prix moyen"], delta=kpis["Intermarche"]["GPLc"]["Classement"], delta_color=kpis["Intermarche"]["GPLc"]["delta_color"])

col_super_u.write("Super U")
col_super_u.metric("Gazole", kpis["Super U"]["Gazole"]["Prix moyen"], delta=kpis["Super U"]["Gazole"]["Classement"], delta_color=kpis["Super U"]["Gazole"]["delta_color"])
col_super_u.metric("SP95", kpis["Super U"]["SP95"]["Prix moyen"], delta=kpis["Super U"]["SP95"]["Classement"], delta_color=kpis["Super U"]["SP95"]["delta_color"])
col_super_u.metric("SP98", kpis["Super U"]["SP98"]["Prix moyen"], delta=kpis["Super U"]["SP98"]["Classement"], delta_color=kpis["Super U"]["SP98"]["delta_color"])
col_super_u.metric("E10", kpis["Super U"]["E10"]["Prix moyen"], delta=kpis["Super U"]["E10"]["Classement"], delta_color=kpis["Super U"]["E10"]["delta_color"])
col_super_u.metric("E85", kpis["Super U"]["E85"]["Prix moyen"], delta=kpis["Super U"]["E85"]["Classement"], delta_color=kpis["Super U"]["E85"]["delta_color"])
col_super_u.metric("GPLc", kpis["Super U"]["GPLc"]["Prix moyen"], delta=kpis["Super U"]["GPLc"]["Classement"], delta_color=kpis["Super U"]["GPLc"]["delta_color"])
