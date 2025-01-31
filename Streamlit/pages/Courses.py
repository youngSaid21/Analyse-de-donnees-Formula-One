import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import timedelta

st.set_page_config(layout="wide")

st.logo("https://1000logos.net/wp-content/uploads/2021/06/F1-logo.png")

# Importer les données
results = pd.read_csv('../Cleaned_Data_Saison/results_2018.csv')
pilotes = pd.read_csv("../Data/drivers.csv")
meteo = pd.read_csv("../Cleaned_Data_Saison/meteo_2018.csv")
courses = pd.read_csv("../Cleaned_Data_Saison/courses_2018.csv")

# Convertir la colonne "time_" en timedelta
results['time_'] = pd.to_timedelta(results['time_'])
# Convertir la colonne "fastestLapTime_" en timedelta
results['fastestLapTime_'] = pd.to_timedelta(results['fastestLapTime_'])
# Convertir la colonne "Time" en timedelta
meteo['Time'] = pd.to_timedelta(meteo['Time'])
# Correspondance des IDs du dataframe meteo avec les resultats
meteo["raceId"] = meteo["Round Number"] + 988  

#print(meteo.head())
#print(meteo.shape)

col1, col2 = st.columns((3,1))

with col1:
	st.title("Courses F1 : Bilan de la Saison 2018")

with col2:
	selected_course = st.selectbox(
	"Séléctionner un Grand Prix",
	courses['name']
)

# Récupérer la course sélectionnée
selected_course_data = courses[courses['name'] == selected_course]

race_results = results[results['raceId'] == int(selected_course_data['raceId'].iloc[0])]

row_col1, row_col2, row_col3, row_col4, row_col5 = st.columns((1, 1, 1, 1, 1))

def create_gauge_chart(value, title, max_range, min_range = 0, color="orange", width=250, height=240):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16}},
        gauge={'axis': {'range': [min_range, max_range]}, 'bar': {'color': color}}
    ))
    fig.update_layout(width=width, height=height)
    return fig

with row_col1:
    # Filtrer le pilote ayant obtenu le plus de points
    top_pilot = race_results[race_results['points'] == race_results['points'].max()]

    # Récupérer le nombre de tours du pilote ayant marqué le plus de points
    laps_top_pilot = top_pilot['laps'].values[0]

    st.plotly_chart(create_gauge_chart(
        value=laps_top_pilot,  # Correction ici
        title="Nombre <br>de tours",
        max_range=21
    ))

with row_col2:
    st.plotly_chart(create_gauge_chart(
        value=race_results['driverId'].nunique(), 
        title="Nombre de <br>pilotes", 
        max_range=20
    ))

with row_col3:
    value_in_hour = race_results['time_'].max().total_seconds() / 3600
    st.plotly_chart(create_gauge_chart(
        value=value_in_hour, 
        title="Durée moyenne <br>de la course (En Heure)", 
        max_range=2, 
        width=265
    ), key="gauge_1")

with row_col4:
    st.plotly_chart(create_gauge_chart(
        value=race_results['fastestLapSpeed_'].max(), 
        title="Vitesse du Meilleur <br>Tour (km/h)", 
        max_range=400
    ))

with row_col5:
    value_in_minutes = race_results['fastestLapTime_'].max().total_seconds() / 60
    st.plotly_chart(create_gauge_chart(
        value=value_in_minutes, 
        title="Durée du Meilleur <br>Tour (minutes)", 
        max_range=2, 
    ))

row2_col1, row2_col2 = st.columns((3,1))

with row2_col1:
	# Joindre les DataFrames results et pilotes sur 'driverId'
	merged_data = pd.merge(race_results[['driverId', 'points']], pilotes[['driverId', 'forename', 'surname']], on='driverId')

	# Calculer les points totaux pour chaque pilote (en regroupant par 'driverId')
	final_standings = merged_data.groupby(['driverId', 'forename', 'surname'])['points'].sum().reset_index()

	# Trier par les points décroissants pour afficher le classement
	final_standings_sorted = final_standings.sort_values(by='points', ascending=True)

	print(final_standings_sorted.head(21))

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
	st.write("### Classement de la course - F1")
	st.plotly_chart(fig)

with row2_col2:
	# Identifier le vainqueur
	winner_id = race_results.loc[race_results["positionOrder"] == 1, "driverId"].values[0]
	winner_info = pilotes[pilotes["driverId"] == winner_id].iloc[0]
	winner_results = race_results[race_results["driverId"] == winner_id].iloc[0]

	# Informations du vainqueur
	winner_name = f"{winner_info['forename']} {winner_info['surname']}"
	winner_points = winner_results["points"]
	winner_nationality = winner_info["nationality"]
	winner_dob = pd.to_datetime(winner_info["dob"])
	winner_age = pd.Timestamp.today().year - winner_dob.year
	winner_time = winner_results["time_"]
	# Extraire l'heure et la minute
	hours = winner_time.seconds // 3600  # Diviser par 3600 pour obtenir l'heure
	minutes = (winner_time.seconds % 3600) // 60  # Récupérer les minutes restante
	winner_fastest_lap_speed = winner_results["fastestLapSpeed_"]
	winner_wikipedia = winner_info["url"]

	winner_image_url = f"../Images/Sebastian.jpg"

	st.write("### 🏆 Leader de la Course")

	st.image(f"../Streamlit/Images/{winner_info['forename']}.jpg")

	st.write(f"🏎 **Pilote :** {winner_name}")
	st.write(f"🌍 **Nationalité :** {winner_nationality}")
	st.write(f"🎂 **Âge :** {winner_age} ans")
	st.write(f"💯 **Points :** {winner_points}")
	st.write(f"⏱ **Temps total de course :** {hours} heure(s) {minutes} minutes(s)")
	st.write(f"🚀 **Vitesse du tour le plus rapide :** {winner_fastest_lap_speed} km/h")
	st.markdown(f"[🔗 Wikipedia]( {winner_wikipedia})")

meteo_race = meteo[meteo['raceId'] == int(selected_course_data['raceId'].iloc[0])]

st.write("### Conditions météorologiques de la course")

row3_col1, row3_col2, row3_col3, row3_col4, row3_col5, row3_col6 = st.columns((1, 1.5, 1.5, 1.5, 1, 1))

with row3_col1:
    rainfall = meteo_race['Rainfall'].unique()
    if rainfall.shape[0] == 2:
        st.metric(
	        label="Météo", 
	        value=f"🌧️🌧️", 
	    )
    else:
    	st.metric(
	        label="Météo", 
	        value=f"☀️☀️", 
	    )

with row3_col2:
    mean_temp = meteo_race['AirTemp'].mean()
    temp_variation = meteo_race['AirTemp'].var()  # Exemple de variation

    st.metric(
        label="Température de l'air (°C)", 
        value=f"{mean_temp:.1f}°C", 
        delta=f"{temp_variation:.1f}°C"
    )

with row3_col3:
    mean_track_temp = meteo_race['TrackTemp'].mean()
    temp_variation = meteo_race['TrackTemp'].var()  # Exemple de variation
    st.metric(
        label="Température de la piste (°C)", 
        value=f"{mean_track_temp:.1f}°C", 
        delta=f"{temp_variation:.1f}°C"
    )

with row3_col4:
    mean_pressure = meteo_race['Pressure'].mean()
    pressure_variation = meteo['Pressure'].var()  # Variation de pression
    st.metric(
        label="Pression atmosphérique (hPa)", 
        value=f"{mean_pressure:.1f} hPa", 
        delta=f"{pressure_variation:.1f} hPa"
    )

with row3_col5:
    mean_humidity = meteo_race['Humidity'].mean()
    humidity_variation = meteo_race['Humidity'].var()  # Variation d'humidité
    st.metric(
        label="Humidité (%)", 
        value=f"{mean_humidity:.1f}%", 
        delta=f"{humidity_variation:.1f}%"
    )


with row3_col6:
    mean_WindSpeed = meteo_race['WindSpeed'].mean()
    WindSpeed_variation = meteo_race['WindSpeed'].var()
    st.metric(
        label="Vitesse du vent (km/h)", 
        value=f"{mean_WindSpeed:.1f}km/h", 
        delta=f"{WindSpeed_variation:.1f}km/h"
    )

st.write("### Variations des Conditions météorologiques pendant la Course")

# Le ID de la course sélectionnée
race_id = selected_course_data['raceId'].iloc[0]

# Filtrer les données météorologiques pour cette course
df_weather = meteo_race[meteo_race['raceId'] == race_id]

if df_weather.empty:
    st.write(f"Aucune donnée météo trouvée pour la course avec l'ID {race_id}.")
else:
    race_name = selected_course_data[selected_course_data['raceId'] == race_id]['name'].iloc[0]

    # Convertir le temps en minutes
    df_weather['TimeMinutes'] = df_weather['Time'].dt.total_seconds() / 60

    # Créer des colonnes pour l'affichage
    col1, col2 = st.columns((1.5,1))

    # 1. Températures de la piste et de l'air
    with col1:
        fig1 = go.Figure()

        # Ajouter la température de la piste
        fig1.add_trace(go.Scatter(
            x=df_weather['TimeMinutes'],
            y=df_weather['TrackTemp'],
            mode='lines',
            name='Température de la piste',  # Légende mise à jour
            line=dict(color='orangered')
        ))

        # Ajouter la température de l'air
        fig1.add_trace(go.Scatter(
            x=df_weather['TimeMinutes'],
            y=df_weather['AirTemp'],
            mode='lines',
            name='Température de l\'air',  # Légende mise à jour
            line=dict(color='orange')
        ))

        # Ajouter les périodes de pluie
        if 'Rainfall' in df_weather.columns and df_weather['Rainfall'].dtype == 'bool':
            rain_periods = df_weather[df_weather['Rainfall'] == True]
            if not rain_periods.empty:
                fig1.add_vrect(
                    x0=rain_periods['TimeMinutes'].min(),
                    x1=rain_periods['TimeMinutes'].max(),
                    fillcolor="orange", opacity=0.2, line_width=0, 
                    annotation_text="Pluie", annotation_position="top left",
                    name="Pluie"
                )

        # Mettre à jour le layout
        fig1.update_layout(
            title=f"Température de la piste et de l'air - {race_name}",
            xaxis_title="Temps (minutes)",
            yaxis_title="Température (°C)",
            legend_title="Légende"
        )

        # Afficher le graphique
        st.plotly_chart(fig1)

    # 2. Humidité
    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_weather['TimeMinutes'], y=df_weather['Humidity'], mode='lines', name='Humidity', line=dict(color='orange')))
        
        fig2.update_layout(title=f"Humidité de la Piste - {race_name}",
                          xaxis_title="Temps (minutes)", yaxis_title="Humidity (%)")

        st.plotly_chart(fig2)

    col3, col4 = st.columns((2,1))

    # 3. Pression atmosphérique
    with col3:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df_weather['TimeMinutes'], y=df_weather['Pressure'], mode='lines', name='Pressure', line=dict(color='orange')))
        
        fig3.update_layout(title=f"Pression Atmosphérique- {race_name}",
                          xaxis_title="Temps (minutes)", yaxis_title="Pressure (mbar)")

        st.plotly_chart(fig3)

    # 4. Direction et vitesse du vent (Windrose)
    with col4:

        fig4 = go.Figure(go.Barpolar(
            r=df_weather['WindSpeed'],  # Vitesse du vent
            theta=df_weather['WindDirection'],  # Direction du vent
            marker=dict(color=df_weather['WindSpeed'], colorscale='oranges'),  # Utilisation d'un dégradé de couleur pour la vitesse
            text=df_weather['WindSpeed'],  # Texte d'information (vitesse du vent)
            opacity=1  # Opacité des barres
        ))

        fig4.update_layout(
            title=f"Direction et Vitesse du Vent - {race_name}",
            polar=dict(
                radialaxis=dict(visible=True, range=[0, df_weather['WindSpeed'].max()]),  # Plage de valeurs du rayon
                bgcolor = "grey"
            ),
            showlegend=False
        )

        #fig4.update_layout(polar_angularaxis_gridcolor="black")



        st.plotly_chart(fig4)
