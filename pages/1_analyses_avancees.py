import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))

from dashboard import DashboardData

st.set_page_config(
    page_title="Analyses Avancees",
    layout="wide"
)

st.markdown("# Analyses Avancees")
st.markdown("Exploration detaillee des donnees")

dashboard = DashboardData()

# Analyse par Département
st.markdown("---")
st.markdown("## Analyse Departementale")

dept_stats = dashboard.get_department_statistics()

if not dept_stats.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Statistiques par Département")
        fig = px.scatter(
            dept_stats,
            x='nb_accidents',
            y='taux_mortalite',
            size='nb_deces',
            color='taux_mortalite',
            color_continuous_scale='Reds',
            hover_data=['dept'],
            title="Relation Accidents-Mortalité par Département",
            labels={
                'nb_accidents': 'Nombre d\'accidents',
                'taux_mortalite': 'Taux mortalité (%)',
                'dept': 'Département'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Details")
        st.dataframe(
            dept_stats.head(10)[['dept', 'nb_accidents', 'nb_deces', 'taux_mortalite']].round(2),
            use_container_width=True
        )

# Conditions d'Eclairage
st.markdown("---")
st.markdown("## Conditions d'Eclairage")

light_analysis = dashboard.get_light_conditions_analysis()

if not light_analysis.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            light_analysis,
            x='condition',
            y='nb_accidents',
            color='taux_mortalite',
            color_continuous_scale='YlOrRd',
            title="Accidents par condition d'éclairage",
            labels={'taux_mortalite': 'Taux mortalité (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Analyse:")
        st.dataframe(light_analysis, use_container_width=True)

# Analyse par Jour
st.markdown("---")
st.markdown("## Analyse par Jour")

day_analysis = dashboard.get_day_analysis()

if not day_analysis.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            day_analysis,
            x='jour_nom',
            y='nb_accidents',
            color='nb_accidents',
            color_continuous_scale='Purples',
            title="Distribution par jour de la semaine"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Jours les plus dangereux:")
        top_days = day_analysis.nlargest(3, 'nb_accidents')
        for idx, row in top_days.iterrows():
            st.metric(
                f"{row['jour_nom']}",
                f"{row['nb_accidents']} accidents",
                f"{row['nb_deces']} deces"
            )

# Analyse Multi-vehicules
st.markdown("---")
st.markdown("## Analyse Multi-vehicules")

vehicle_analysis = dashboard.get_vehicle_analysis()

if not vehicle_analysis.empty:
    fig = px.scatter(
        vehicle_analysis,
        x='nb_vehicules',
        y='taux_mortalite',
        size='nb_accidents',
        color='nb_deces',
        color_continuous_scale='Reds',
        title="Risque en fonction du nombre de vehicules impliques",
        labels={
            'nb_vehicules': 'Nombre de vehicules',
            'taux_mortalite': 'Taux mortalite (%)',
            'nb_accidents': 'Nombre d\'accidents',
            'nb_deces': 'Deces'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("Plus le nombre de vehicules augmente, plus le taux de mortalite tend a augmenter.")

# Rapport de Qualite des Donnees
st.markdown("---")
st.markdown("## Rapport de Qualite des Donnees")

quality = dashboard.get_data_quality_report()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Accidents", quality['total_accidents'])

with col2:
    st.metric("Plage de dates", quality['date_range'])

with col3:
    st.metric("Départements uniques", quality['departments_count'])
