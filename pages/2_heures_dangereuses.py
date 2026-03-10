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
    page_title="Heures Dangereuses",
    layout="wide"
)

st.markdown("# Heures les Plus Dangereuses")
st.markdown("Analyse des risques horaires")

dashboard = DashboardData()

# Heures a Risque Maximal
st.markdown("## Heures a Risque Maximal")

high_risk = dashboard.get_high_risk_hours()

if not high_risk.empty:
    col1, col2, col3 = st.columns(3)
    
    top_hour = high_risk.index[0]
    with col1:
        st.metric(
            "Heure la plus critique",
            f"{top_hour}h00",
            f"Taux mortalite: {high_risk['taux_mortalite'].iloc[0]:.1f}%"
        )
    
    with col2:
        st.metric(
            f"Accidents a {top_hour}h",
            f"{high_risk['nb_accidents'].iloc[0]:.0f}",
            f"Deces: {high_risk['nb_deces'].iloc[0]:.0f}"
        )
    
    with col3:
        avg_rate = high_risk['taux_mortalite'].mean()
        st.metric(
            "Taux moyen top 5 heures",
            f"{avg_rate:.2f}%"
        )

# Distribution Horaire Complète
st.markdown("---")
st.markdown("## Distribution Horaire")

hourly = dashboard.get_hourly_distribution()

if not hourly.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            hourly,
            x='heure',
            y='nb_accidents',
            color='nb_accidents',
            color_continuous_scale=['green', 'yellow', 'orange', 'red'],
            title="Nombre d'accidents par heure",
            labels={'heure': 'Heure du jour', 'nb_accidents': "Nombre d'accidents"}
        )
        fig.update_layout(height=400, xaxis=dict(tickmode='linear', tick0=0, dtick=1))
        st.plotly_chart(fig, use_container_width=True)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly['heure'],
            y=hourly['nb_accidents'],
            fill='tozeroy',
            mode='lines+markers',
            name='Accidents',
            line=dict(color='#ff4b4b', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title="Intensité par heure (courbe)",
            xaxis_title="Heure",
            yaxis_title="Nombre d'accidents",
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Heures de Pointe
st.markdown("---")
st.markdown("## Heures de Pointe")

peak_hours = hourly.nlargest(5, 'nb_accidents')

for idx, row in peak_hours.iterrows():
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.subheader(f"{int(row['heure']):02d}h00")
        with col2:
            st.progress(row['nb_accidents'] / hourly['nb_accidents'].max())
        with col3:
            st.metric(f"Accidents", f"{int(row['nb_accidents'])}")

# Recommandations
st.markdown("---")
st.markdown("## Recommandations")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Conseils pour conducteurs
    - Eviter trajets entre 07h-09h
    - Vigilance entre 17h-20h
    - Reposer regulierement
    """)

with col2:
    st.markdown("""
    ### Pour les autorites
    - Augmenter presence policiere
    - Campagnes de sensibilisation
    - Renforcer controles de vitesse
    """)

with col3:
    st.markdown("""
    ### Pour les entreprises
    - Adapter horaires de travail
    - Encourager teletravail aux heures de pointe
    - Formations securite routiere
    """)

# Donnees detaillees
st.markdown("---")
st.markdown("## Donnees Detaillees par Heure")

with st.expander("Voir tous les horaires"):
    st.dataframe(hourly.sort_values('heure'), use_container_width=True)
