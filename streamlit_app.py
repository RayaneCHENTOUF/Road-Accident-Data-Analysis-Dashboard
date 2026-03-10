import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Ajouter les dossiers au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    from config.config import config
    from dashboard import DashboardData
except ImportError as e:
    st.error(f"Erreur d'import : {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="Accidents Routiers Dashboard",
    layout="wide"
)

# Simple styling
st.markdown("""
<style>
body {
    font-family: 'Arial', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# Dashboard - Accidents Routiers")
st.markdown("Analyse des donnees 2023")

# Initialize dashboard
dashboard_data = DashboardData()

with st.sidebar:
    st.markdown("## Filtres")
    
    if not dashboard_data.connected:
        st.warning("Base de donnees hors ligne - Mode CSV")
    
    available_months = dashboard_data.get_available_months()
    available_depts = dashboard_data.get_available_departments()
    
    selected_months = st.multiselect(
        "Mois",
        options=available_months,
        default=available_months
    )
    
    selected_depts = st.multiselect(
        "Departements",
        options=available_depts,
        default=available_depts[:5] if available_depts else []
    )
    
    filters = {
        'months': selected_months if selected_months else available_months,
        'departments': selected_depts if selected_depts else available_depts
    }

# KPIs
st.markdown("---")
st.markdown("## Indicateurs Cles")

kpis = dashboard_data.get_kpis(filters)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Accidents",
        f"{kpis['total_accidents']:,}"
    )

with col2:
    st.metric(
        "Deces",
        f"{kpis['total_deaths']}",
        delta=f"Taux: {kpis['death_rate']:.2f}%"
    )

with col3:
    st.metric(
        "Blesses Graves",
        f"{kpis['serious_injured']}"
    )

with col4:
    st.metric(
        "Blesses Legers",
        f"{kpis['light_injured']}"
    )

with col5:
    st.metric(
        "Vehicules",
        f"{kpis['total_vehicles']:,}"
    )

# Main Charts
st.markdown("---")
st.markdown("## Analyses Principales")

col1, col2 = st.columns([2, 1])

# Evolution temporelle
with col1:
    st.subheader("Evolution Mensuelle")
    monthly_data = dashboard_data.get_monthly_evolution(filters)
    
    if not monthly_data.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['mois'],
            y=monthly_data['nb_accidents'],
            mode='lines+markers',
            name='Accidents',
            line=dict(color='#ff4b4b', width=3),
            marker=dict(size=10)
        ))
        
        fig.add_trace(go.Bar(
            x=monthly_data['mois'],
            y=monthly_data['nb_deces'],
            name='Deces',
            marker=dict(color='#8b0000'),
            opacity=0.3,
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Accidents et Deces par Mois",
            xaxis_title="Mois",
            yaxis_title="Nombre d'accidents",
            yaxis2=dict(title="Nombre de deces", overlaying='y', side='right'),
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnee pour les filtres selectionnes")

# Distribution gravite
with col2:
    st.subheader("Gravite")
    gravity = dashboard_data.get_gravity_distribution(filters)
    
    if not gravity.empty:
        colors = ['#90EE90', '#FFD700', '#FF6B6B']
        fig = px.pie(
            gravity,
            values='nombre',
            names='gravite',
            color_discrete_sequence=colors,
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# Row 2: Heures + Jours
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution Horaire")
    hourly = dashboard_data.get_hourly_distribution(filters)
    
    if not hourly.empty:
        fig = px.bar(
            hourly,
            x='heure',
            y='nb_accidents',
            title="Accidents par heure",
            color='nb_accidents',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Conditions d'Eclairage")
    light_analysis = dashboard_data.get_light_conditions_analysis()
    
    if not light_analysis.empty:
        fig = px.bar(
            light_analysis,
            x='condition',
            y='nb_accidents',
            color='taux_mortalite',
            color_continuous_scale='YlOrRd',
            title="Accidents par condition d'eclairage",
            labels={'taux_mortalite': 'Taux mortalite (%)'}
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# Row 3: Top Departments + Vehicle Analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("Departements les Plus Touches")
    dept_data = dashboard_data.get_top_departments(filters, limit=10)
    
    if not dept_data.empty:
        fig = px.bar(
            dept_data,
            x='nb_accidents',
            y='departement',
            orientation='h',
            title="Top 10 des departements",
            color='nb_accidents',
            color_continuous_scale='Reds',
            text='nb_accidents'
        )
        fig.update_layout(
            height=350,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Analyse par Nombre de Vehicules")
    vehicle_analysis = dashboard_data.get_vehicle_analysis()
    
    if not vehicle_analysis.empty:
        fig = px.scatter(
            vehicle_analysis,
            x='nb_vehicules',
            y='taux_mortalite',
            size='nb_accidents',
            color='nb_accidents',
            color_continuous_scale='Oranges',
            title="Risque vs Nombre de vehicules",
            labels={
                'nb_vehicules': 'Nombre de vehicules',
                'taux_mortalite': 'Taux de mortalite (%)',
                'nb_accidents': 'Nombre d\'accidents'
            }
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("---")
st.markdown("## Insights et Recommandations")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Heures a Risque")
    high_risk = dashboard_data.get_high_risk_hours()
    if not high_risk.empty:
        st.write(f"Heure critique: {high_risk.index[0]}h00")
        st.write(f"Taux mortalite: {high_risk['taux_mortalite'].iloc[0]:.1f}%")

with col2:
    st.subheader("Qualite des Donnees")
    quality = dashboard_data.get_data_quality_report()
    st.write(f"Accidents: {quality['total_accidents']}")
    st.write(f"Departements: {quality['departments_count']}")

with col3:
    st.subheader("Statistiques Globales")
    summary = dashboard_data.get_summary_stats()
    st.write(f"Usagers: {summary['Total usagers touches']:,}")
    st.write(f"Mortalite: {summary['Taux de mortalite']}")

# Data table
st.markdown("---")
st.markdown("## Donnees Brutes")

with st.expander("Voir les donnees brutes"):
    st.dataframe(dashboard_data.df_characteristics, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
Dashboard cree avec Streamlit | Donnees: BAAC 2023 | Visualisations: Plotly
""")

