import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(layout="wide")

st.logo("https://1000logos.net/wp-content/uploads/2021/06/F1-logo.png")

st.title("Tableau de bord : Formula One Saison 2018")

# Importer les données
results = pd.read_csv('../Cleaned_Data_Saison/results_2018.csv')
pilotes = pd.read_csv("../Data/drivers.csv")
meteo = pd.read_csv("../Cleaned_Data_Saison/meteo_2018.csv")

# Convertir la colonne "time_" en timedelta
results['time_'] = pd.to_timedelta(results['time_'])
# Convertir la colonne "fastestLapTime_" en timedelta
results['fastestLapTime_'] = pd.to_timedelta(results['fastestLapTime_'])

print(results.head())
print(meteo.head())
print(pilotes.head())

col1, col2, col3, col4, col5 = st.columns((1, 1, 1, 1, 1))

def create_gauge_chart(value, title, max_range, color="orange", width=250, height=230):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16}},
        gauge={'axis': {'range': [0, max_range]}, 'bar': {'color': color}}
    ))
    fig.update_layout(width=width, height=height)
    return fig

with col1:
    st.plotly_chart(create_gauge_chart(
        value=results['raceId'].nunique(), 
        title="Nombre de Grands <br> Prix", 
        max_range=21
    ))

with col2:
    st.plotly_chart(create_gauge_chart(
        value=results['driverId'].nunique(), 
        title="Nombre de <br> pilotes", 
        max_range=20
    ))

with col3:
    value_in_hour = results['time_'].max().total_seconds() / 3600
    st.plotly_chart(create_gauge_chart(
        value=value_in_hour, 
        title="Durée moyenne <br>d'une course (En Heure)", 
        max_range=2, 
        width=265
    ), key="gauge_1")

with col4:
    st.plotly_chart(create_gauge_chart(
        value=results['fastestLapSpeed_'].max(), 
        title="Vitesse du Meilleur<br> Tour (km/h)", 
        max_range=400
    ))

with col5:
    value_in_minutes = results['fastestLapTime_'].max().total_seconds() / 60
    st.plotly_chart(create_gauge_chart(
        value=value_in_minutes, 
        title="Durée du Meilleur <br>Tour (minutes)", 
        max_range=2, 
    ))

row2_col1, row2_col2 = st.columns((3, 1))

with row2_col1:
    # Données des Grands Prix 2018
    gp_data = {
        'Ville': [
            'Melbourne', 'Sakhir', 'Shanghai', 'Baku', 'Barcelona', 'Monaco', 'Montreal', 
            'Le Castellet', 'Spielberg', 'Silverstone', 'Hockenheim', 'Budapest', 'Spa-Francorchamps', 
            'Monza', 'Singapore', 'Sochi', 'Suzuka', 'Austin', 'Mexico City', 'São Paulo', 'Abu Dhabi'
        ],
        'Pays': [
            'Australie', 'Bahreïn', 'Chine', 'Azerbaïdjan', 'Espagne', 'Monaco', 'Canada', 'France', 
            'Autriche', 'Royaume-Uni', 'Allemagne', 'Hongrie', 'Belgique', 'Italie', 'Singapour', 'Russie', 
            'Japon', 'États-Unis', 'Mexique', 'Brésil', 'Émirats Arabes Unis'
        ],
        'Latitude': [
            -37.8172, 26.0275, 31.2786, 40.3725, 41.5797, 43.7347, 45.5088, 44.2764, 47.2194, 52.0737, 48.5592, 
            47.6240, 50.4370, 45.6319, 1.2950, 43.6020, 52.2170, 34.7416, 19.4326, -23.5505, 24.4675
        ],
        'Longitude': [
            144.9559, 50.5106, 121.3997, 49.8670, 2.2735, 7.4268, -73.5618, 5.1185, 15.5136, -1.0297, 9.0067, 
            19.0423, 4.4391, 9.2814, 103.8675, 39.7215, 137.7315, -97.6417, -99.1332, -46.6333, 54.6034
        ],
        'URL': [
            'http://en.wikipedia.org/wiki/2018_Australian_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Bahrain_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Chinese_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Azerbaijan_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Spanish_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Monaco_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Canadian_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_French_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Austrian_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_British_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_German_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Hungarian_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Belgian_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Italian_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Singapore_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Russian_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Japanese_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_United_States_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Mexican_Grand_Prix', 'http://en.wikipedia.org/wiki/2018_Brazilian_Grand_Prix', 
            'http://en.wikipedia.org/wiki/2018_Abu_Dhabi_Grand_Prix'
        ]
    }

    # Créer un DataFrame
    df = pd.DataFrame(gp_data)

    # Créer une carte centrée sur le monde
    m = folium.Map(location=[20, 0], zoom_start=1)

    # Créer un cluster pour mieux gérer les marqueurs
    marker_cluster = MarkerCluster().add_to(m)

    # Ajouter les marqueurs pour chaque ville
    for i, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Ville']}</b><br><a href='{row['URL']}'>Voir la course</a>",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    # Afficher la carte dans Streamlit
    st.write("### Répartition Géographique des Grands Prix")
    st.components.v1.html(m._repr_html_(), height=500)

with row2_col2:
    # Données du barème des points
    data = {
        "Position": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Points": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
        "Tour le plus rapide": ["1 point (si top 10)", "", "", "", "", "", "", "", "", ""]
    }

    # Créer un DataFrame
    df = pd.DataFrame(data)

    # Afficher le tableau dans Streamlit
    st.write("### Barème des Points - Saison 2018")
    st.dataframe(df, use_container_width=True)

row3_col1, row3_col2 = st.columns((3, 1))

with row3_col1:
    # Joindre les DataFrames results et pilotes sur 'driverId'
    merged_data = pd.merge(results[['driverId', 'points']], pilotes[['driverId', 'forename', 'surname']], on='driverId')

    # Calculer les points totaux pour chaque pilote (en regroupant par 'driverId')
    final_standings = merged_data.groupby(['driverId', 'forename', 'surname'])['points'].sum().reset_index()

    # Trier par les points décroissants pour afficher le classement
    final_standings_sorted = final_standings.sort_values(by='points', ascending=True)

    # Créer un graphique interactif avec Plotly
    fig = px.bar(final_standings_sorted, 
                 y=final_standings_sorted['forename'] + ' ' + final_standings_sorted['surname'], 
                 x=final_standings_sorted['points'], 
                 orientation='h',
                 title=None,
                 labels={"forename": "Pilote", "points": "Points"},
                 color="points",  # Colorer selon les points
                 color_continuous_scale="oranges",  # Palette de couleurs
                 text="points",  # Afficher les points sur chaque barre
                 template="plotly_dark",  # Utilisation d'un thème moderne et sombre
                 category_orders={'forename': final_standings_sorted['forename'].iloc[::-1].values}  # Inverser l'ordre des catégories
                )

    # Personnaliser les axes et le design
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0, 0.3)",  # Changer l'arrière-plan global en noir
        plot_bgcolor="rgba(0,0,0,0)",  # Rendre le fond du graphe transparent
        xaxis_title="Points",
        yaxis_title="Pilote",
        margin=dict(l=100, r=50, t=100, b=50),  # Ajouter des marges pour plus d'espace
        height=600  # Ajuster la taille
    )

    # Afficher le graphique interactif dans Streamlit
    st.write("### Classement Final de la Saison 2018 - F1")
    st.plotly_chart(fig)

with row3_col2:
    # Infos du champion 2018 (Lewis Hamilton)
    champion_name = "Lewis Hamilton"
    champion_nationality = "Britannique"
    nationality_flag_url = "https://upload.wikimedia.org/wikipedia/en/a/ae/Flag_of_the_United_Kingdom.svg"  # Drapeau UK
    champion_image_url = "https://cdn-2.motorsport.com/images/mgl/YEQ1pGwY/s8/lewis-hamilton-mercedes.jpg"  # Photo Hamilton

    # Records de la saison 2018
    records = {
        "Écurie": "Mercedes",
        "Courses disputées": 21,
        "Victoires": 11,
        "Podiums": 17,
        "Pole positions": 11,
        "Points": 408
    }

    # Affichage dans la colonne
    with row3_col2:
        st.markdown("### 🏆 Vainqueur de la saison")
        
        # Afficher la photo du champion
        st.image(champion_image_url, width=300, caption=champion_name, use_container_width=True)

        # Afficher la nationalité avec un petit drapeau
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(nationality_flag_url, width=50, use_container_width=True)  # Drapeau
        with col2:
            st.write(f"**Nationalité :** {champion_nationality}")

        # Afficher les records sous forme de tableau
        st.markdown("#### 📊 Statistiques de la saison")
        st.dataframe(records, use_container_width=True)

# Création de la colonne fullname pour les pilotes
pilotes["fullname"] = pilotes["forename"] + " " + pilotes["surname"]

# Associer meteo et results via raceId
meteo_summary = meteo.groupby("Round Number")["Rainfall"].max().reset_index()
meteo_summary["raceId"] = meteo_summary["Round Number"] + 988  # Correspondance des IDs
results_with_meteo = results.merge(meteo_summary[['raceId', 'Rainfall']], on="raceId", how="left")

# Calcul des points selon la météo
comparaison = (
    results_with_meteo.groupby(['driverId', 'Rainfall'])['points']
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

# Renommer les colonnes
comparaison.columns = ['driverId', 'points_sans_pluie', 'points_avec_pluie']

# Fusion avec les noms des pilotes
comparaison = comparaison.merge(pilotes[['driverId', 'fullname']], on='driverId', how='left')

# Calcul du total des points et tri
comparaison['points_totaux'] = comparaison['points_sans_pluie'] + comparaison['points_avec_pluie']
comparaison_triee = comparaison.sort_values(by='points_totaux', ascending=True)

# Transformation des données pour Plotly
comparaison_long = comparaison_triee.melt(
    id_vars=["fullname"],  
    value_vars=["points_sans_pluie", "points_avec_pluie"], 
    var_name="Condition", 
    value_name="Points"
)

# Mapper les valeurs pour un affichage plus clair
condition_mapping = {"points_sans_pluie": "Courses Sèches", "points_avec_pluie": "Courses Pluvieuses"}
comparaison_long["Condition"] = comparaison_long["Condition"].map(condition_mapping)

st.write("### Classement Final de la Saison 2018 en Fonction de la Pluie 🌦️🏎️")

# Création du graphique interactif avec Plotly
fig = px.bar(
    comparaison_long, 
    y="fullname",  
    x="Points", 
    color="Condition",
    barmode="group",
    labels={"Condition": "Conditions de Course", "Points": "Points", "fullname": "Pilotes"},
    title=None,
    height=600,
    orientation="h",
    color_discrete_map={
        "Courses Sèches": "orange",
        "Courses Pluvieuses": "red" 
    }
)

# Affichage du graphique interactif
st.plotly_chart(fig, use_container_width=True)