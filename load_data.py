from os import rename
import pandas as pd
import numpy as np
from unidecode import unidecode
import os, json
import math 
from tqdm import tqdm

def rename_enseigne(df, search_term, new_name):
    df['Enseignes'] = df['Enseignes'].str.replace(search_term, new_name)

def load_station():
    # Load data
    df_station = pd.read_csv("./data/Infos_Stations.csv", dtype={'ID':str, 'Enseignes': str})
    # remove accents, titlecase 
    df_station['Enseignes'] = df_station['Enseignes'].apply(lambda x: unidecode(x))
    df_station['Enseignes'] = df_station['Enseignes'].str.replace('i? 1/2', 'e')
    df_station['Enseignes'] = df_station['Enseignes'].str.title()

    # Latitude and Longitude to float
    df_station['Latitude'] = df_station['Latitude'].apply(lambda x: x/100000)
    df_station['Longitude'] = df_station['Longitude'].apply(lambda x: x/100000)

    # Rename 
    rename_enseigne(df_station, 'Total Redon', 'Total')
    rename_enseigne(df_station, 'Total Energie', 'Total')
    rename_enseigne(df_station, 'Totalenergie', 'Total')
    rename_enseigne(df_station, 'Total Contact', 'Total')
    rename_enseigne(df_station, 'Totalenergie', 'Total')
    rename_enseigne(df_station, 'Totals', 'Total')
    rename_enseigne(df_station, 'Carrefour Market', 'Carrefour')
    rename_enseigne(df_station, 'Carrefour Express', 'Carrefour')
    rename_enseigne(df_station, 'Carrefour Contact', 'Carrefour')
    rename_enseigne(df_station, 'Carrefour Contact', 'Carrefour')
    rename_enseigne(df_station, 'U express', 'Super U')
    rename_enseigne(df_station, 'U Express', 'Super U')
    rename_enseigne(df_station, 'SUPER U', 'Super U')
    rename_enseigne(df_station, 'System U', 'Super U')
    rename_enseigne(df_station, 'Systeme U', 'Super U')
    rename_enseigne(df_station, 'Station U', 'Super U')
    rename_enseigne(df_station, 'Intermarche Contact', 'Intermarche')
    rename_enseigne(df_station, 'Super Casino', 'Casino')
    rename_enseigne(df_station, 'Independant Sans Enseigne', 'Independant')
    rename_enseigne(df_station, 'Inda(C)Pendant Sans Enseigne', 'Independant')
    rename_enseigne(df_station, 'Esso Express', 'Esso')
    return df_station

def load_price():
    # Load data
    df_price = pd.read_csv("./data/Prix_2024_2semaines.csv", dtype={'id':str, 'Date':str})
    # Date to datetime
    df_price['Date'] = pd.to_datetime(df_price['Date'], format='%Y-%m-%d')
    # Supprime valeur inférieur à 0
    df_price = df_price[(df_price['Gazole']>=0) & (df_price['SP95']>=0) & (df_price['SP98']>=0) & (df_price['E10']>=0) & (df_price['E85']>=0) & (df_price['GPLc']>=0)]
    return df_price

def load_data(df_station=load_station(), df_price=load_price()):

    if os.path.exists('./data/data.csv'):
        df = pd.read_csv('./data/data.csv', dtype={'ID':str, 'Date':str})
        df["Date"] = pd.to_datetime(df["Date"], format='%Y-%m-%d')
        return df
    
    df = pd.merge(df_station, df_price, left_on="ID", right_on="id")
    df = df.dropna()

    # Drop colonne id
    df = df.drop(columns=['id'])

    # Garder les enseignes qui possèdent plus de 100 stations
    enseigne_count = df_station['Enseignes'].value_counts()
    enseigne_count = enseigne_count[enseigne_count>100].index.tolist()
    enseigne_count = set(enseigne_count) - set(['Autre', 'Inconnu', 'Independant']) # Exclure les enseigne independant, autre, inconnu
    df = df[df['Enseignes'].isin(list(enseigne_count))]

    # Remplacer les valeurs abérrantes par le quartile correspondant
    def cap_quantiles(group):
        for col in ['Gazole', 'SP95', 'SP98', 'E10', 'E85', 'GPLc']:
            q1 = group[col].quantile(0.25)
            q3 = group[col].quantile(0.75)
            group[col] = np.where((group[col] < q1) & (group[col] > 0), q1, group[col])
            group[col] = np.where(group[col] > q3, q3, group[col])
        return group
    df = df.groupby('ID').apply(cap_quantiles)

    # Sauvegarde des données
    df.to_csv('./data/data.csv', index=False)


    return df

def load_concurrents(df_station=load_station()):
    if os.path.exists('./data/concurrents.json'):
        with open('./data/concurrents.json', 'r') as f:
            return json.load(f)

    id_coord_carrefour = dict_id_coord(df_station[df_station['Enseignes']=='Carrefour'])
    id_coord = dict_id_coord(df_station[df_station['Enseignes']!='Carrefour'])

    concurrents = {}
    for id_carrefour, coord_carrefour in tqdm(id_coord_carrefour.items()):
        concurrents[id_carrefour] = get_concurrents(id_coord, coord_carrefour[0], coord_carrefour[1], id_carrefour)

    with open('./data/concurrents.json', 'w') as f:
        json.dump(concurrents, f)
    
    return concurrents


def haversine(lat1, lon1, lat2, lon2):
    # Convertir les degrés en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # Rayon moyen de la Terre en kilomètres
    R = 6371.0
    # Différences de coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # Formule de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon /
    2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Distance en kilomètres
    distance = R * c
    return distance

def get_concurrents(dict_id, lat, lon, id_carrefour):
    concurrents = {}
    for id, coord in dict_id.items():
        if id != id_carrefour:
            distance = haversine(lat, lon, coord[0], coord[1])
            if distance <= 10:
                concurrents[id] = distance
    return concurrents

# Calcul des concurrents pour toute les stations Carrefour
def dict_id_coord(df):
    id_coord = {}
    for i, row in tqdm(df.iterrows()):
        id_coord[row['ID']] = (row['Latitude'], row['Longitude'])
    return id_coord
