import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide")

st.logo("https://1000logos.net/wp-content/uploads/2021/06/F1-logo.png")

# Importer les données
results = pd.read_csv('/mount/src/analyse-de-donnees-formula-one/Cleaned_Data_Saison/results_2018.csv')
pilotes = pd.read_csv("/mount/src/analyse-de-donnees-formula-one/Data/drivers.csv")
meteo = pd.read_csv("/mount/src/analyse-de-donnees-formula-one/Cleaned_Data_Saison/meteo_2018.csv")
courses = pd.read_csv("/mount/src/analyse-de-donnees-formula-one/Cleaned_Data_Saison/courses_2018.csv")

# Convertir la colonne "time_" en timedelta
results['time_'] = pd.to_timedelta(results['time_'])

# Convertir la colonne "fastestLapTime_" en timedelta
results['fastestLapTime_'] = pd.to_timedelta(results['fastestLapTime_'])

# Convertir la colonne "Time" en timedelta
meteo['Time'] = pd.to_timedelta(meteo['Time'])

# Correspondance des IDs du dataframe meteo avec les resultats
meteo["raceId"] = meteo["Round Number"] + 988 

# Garder uniquement les pilotes dont l'ID est présent dans les résultats
pilotes_filtered = pilotes[pilotes['driverId'].isin(results['driverId'])]

# Fusionner le nom et prenom du pilote
pilotes_filtered['fullname'] = pilotes_filtered['forename'] + " " + pilotes_filtered['surname']

#print(courses.head())
#print(results.head())

col1, col2 = st.columns((3,1))

with col1:
	st.title("Pilotes F1 : Bilan de la Saison 2018")

with col2:
	selected_driver = st.selectbox(
	"Séléctionner un pilote",
	pilotes_filtered['fullname']
)

row1_col1, row2_col2 = st.columns((3,1.2))

# Récupérer le pilote sélectionnée
selected_driver_data = pilotes_filtered[pilotes_filtered['fullname'] == selected_driver]

# Extraire l'ID du pilote (prendre le premier élément avec iloc[0])
driver_id = selected_driver_data['driverId'].iloc[0]

# Filtrer les résultats pour ce pilote
driver_results = results[results['driverId'] == driver_id]

# Joindre avec la table 'courses' pour ajouter le nom du Grand Prix
driver_results = driver_results.merge(courses[['raceId', 'name']], on='raceId', how='left')

# Trier par la course (pour l'ordre des courses)
driver_results = driver_results.sort_values(by="raceId")

print(driver_results.head())

# Extraire les points et les noms des courses
race_names = driver_results['name']
points = driver_results['points']

with row1_col1:

	# Créer un graphique interactif avec Plotly
	fig = px.line(driver_results, x='name', y='points', title=None)
	
	# Mettre à jour la couleur de la ligne	
	fig.update_traces(line=dict(color='orange'))

	# Ajouter des labels aux axes
	fig.update_layout(
	    xaxis_title="Grand Prix",
	    yaxis_title="Points",
	    xaxis=dict(tickmode='array', tickvals=race_names, ticktext=race_names)  # Afficher les noms des courses sur l'axe X
	)

	st.write(f"### Points gagnés par le pilote {selected_driver} au cours de la saison 2018")
	# Afficher le graphique dans Streamlit
	st.plotly_chart(fig)

with row2_col2:
	# Déterminer l'age du pilote
	driver_age_dob = pd.to_datetime(selected_driver_data["dob"].iloc[0])
	driver_age = pd.Timestamp.today().year - driver_age_dob.year

	# Calcul du classement final de la saison
	season_standings = results.groupby("driverId")["points"].sum().reset_index()

	# Trier les pilotes en fonction du total des points (ordre décroissant)
	season_standings = season_standings.sort_values(by="points", ascending=False).reset_index(drop=True)

	# Ajouter une colonne de classement
	season_standings["rank_final"] = season_standings.index + 1

	# Trouver le rang du pilote sélectionné
	final_rank = season_standings.loc[season_standings["driverId"] == driver_id, "rank_final"].values[0]

	

	#print(driver_results.head())

	st.write("### 🏁 Informations du pilote")

	st.image(f"/mount/src/analyse-de-donnees-formula-one/Streamlit/Images/{selected_driver_data['forename'].iloc[0]}.jpg")
	st.write(f"🏎 **Pilote :** {selected_driver_data['fullname'].iloc[0]}")
	st.write(f"🌍 **Nationalité :** {selected_driver_data['nationality'].iloc[0]}")
	st.write(f"🎂 **Âge :** {driver_age} ans")
	st.write(f"🏆 **Classement final de la saison :** {final_rank}ᵉ")
	st.write(f"💯 **Points :** {driver_results['points'].sum()}")
	#st.write(f"⏱ **Temps total de course :** {hours} heure(s) {minutes} minutes(s)")
	st.write(f"🚀 **Vitesse du tour le plus rapide :** {driver_results['fastestLapSpeed_'].max()} km/h")
	st.markdown(f"[🔗 Wikipedia]( {selected_driver_data['url'].iloc[0]})")

# Création de la colonne fullname pour les pilotes
pilotes["fullname"] = pilotes["forename"] + " " + pilotes["surname"]

# Associer meteo et results via raceId
meteo_summary = meteo.groupby("Round Number")["Rainfall"].max().reset_index()
meteo_summary["raceId"] = meteo_summary["Round Number"] + 988  # Correspondance des IDs
drivers_results_with_meteo = driver_results.merge(meteo_summary[['raceId', 'Rainfall']], on="raceId", how="left")

# Calcul des points selon la météo
comparaison = (
    drivers_results_with_meteo.groupby(['driverId', 'Rainfall'])['points']
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

# Filtrer les résultats pour le pilote sélectionné
drivers_results_with_meteo = drivers_results_with_meteo[drivers_results_with_meteo["driverId"] == driver_id]

# Ajouter la colonne Condition en fonction de la pluie
driver_results["Condition"] = drivers_results_with_meteo["Rainfall"].apply(lambda x: "Courses Pluvieuses" if x else "Courses Sèches")

# Trier les courses par raceId pour un affichage logique
driver_results = driver_results.sort_values(by="raceId")

# Séparer les courses pluvieuses et sèches
driver_results_rain = driver_results[driver_results["Condition"] == "Courses Pluvieuses"]
driver_results_dry = driver_results[driver_results["Condition"] == "Courses Sèches"]

# Sélectionner les colonnes nécessaires pour chaque condition
driver_results_rain_long = driver_results_rain[["name", "points", "Condition"]]
driver_results_dry_long = driver_results_dry[["name", "points", "Condition"]]

row3_col1, row3_col2 = st.columns((3,1.2))

with row3_col1:

	# Graphique pour les courses sèches
	st.write(f"### Évolution des points du pilote {selected_driver} en **courses sèches** ☀️")

	fig_dry = px.line(
	    driver_results_dry_long, 
	    x="name",  
	    y="points", 
	    color="Condition",
	    markers=True,
	    labels={"name": "Grand Prix", "points": "Points Gagnés", "Condition": "Conditions de Course"},
	    title=None,
	    color_discrete_map={"Courses Sèches": "orange"}
	)

	st.plotly_chart(fig_dry, use_container_width=True)

	# Graphique pour les courses pluvieuses
	st.write(f"### Évolution des points du pilote {selected_driver} en **courses pluvieuses** 🌧️")

	fig_rain = px.line(
	    driver_results_rain_long, 
	    x="name",  
	    y="points", 
	    color="Condition",
	    markers=True,
	    labels={"name": "Grand Prix", "points": "Points Gagnés", "Condition": "Conditions de Course"},
	    title=None,
	    color_discrete_map={"Courses Pluvieuses": "red"}
	)

	st.plotly_chart(fig_rain, use_container_width=True)

with row3_col2:

	# Regrouper les données par condition et calculer la somme des points
	points_by_condition = driver_results.groupby("Condition")["points"].sum().reset_index()

	# Création du graphique interactif
	fig = px.bar(
	    points_by_condition, 
	    x="Condition", 
	    y="points", 
	    color="Condition", 
	    color_discrete_map={"Courses Pluvieuses": "red", "Courses Sèches": "orange"},
	    labels={"Condition": "Condition de la course", "points": "Total des points"},
	    title=None,
	    #height=600,
	    text_auto=True
	)

	st.write(f"### Nombre total de points du pilote {selected_driver} par condition météo")
	# Affichage du graphique interactif dans Streamlit
	st.plotly_chart(fig, use_container_width=True)

