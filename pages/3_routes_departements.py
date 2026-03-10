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
    page_title="Routes et Departements",
    layout="wide"
)

st.markdown("# Analyse Routes et Departements")
st.markdown("Analyse des accidents par routes et departements")

dashboard = DashboardData()

# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "Routes",
    "Departements", 
    "Croisement",
    "Hotspots"
])

# TAB 1: ROUTES
with tab1:
    st.markdown("## Top Routes par Accidents")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        road_data = dashboard.get_accidents_by_road(limit=15)
        
        if not road_data.empty:
            fig = px.bar(
                road_data,
                x='nb_accidents',
                y='adr',
                orientation='h',
                color='taux_mortalite',
                color_continuous_scale='Reds',
                title="Top 15 Routes - Nombre d'accidents",
                labels={
                    'adr': 'Route/Adresse',
                    'nb_accidents': "Nombre d'accidents",
                    'taux_mortalite': 'Taux mortalite (%)'
                }
            )
            fig.update_traces(text=road_data['nb_accidents'], textposition='outside')
            fig.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Nombre d'accidents",
                yaxis_title="Route"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Statistiques Routes")
        all_roads = dashboard.get_road_statistics()
        
        st.metric("Total routes concernees", len(all_roads))
        st.metric("Route la plus dangereuse", 
                 f"{road_data.iloc[0]['adr']}" if not road_data.empty else "N/A")
        st.metric("Accidents sur top route",
                 f"{int(road_data.iloc[0]['nb_accidents'])}" if not road_data.empty else "0")
        
        # Top route risk
        if not all_roads.empty:
            top_risk = all_roads.nlargest(1, 'taux_mortalite').iloc[0]
            st.metric("Route a plus haut risque de mortalite",
                     f"{top_risk['route']}",
                     f"Taux: {top_risk['taux_mortalite']:.1f}%")

# TAB 2: DEPARTEMENTS
with tab2:
    st.markdown("## Analyse par Departement")
    
    dept_detailed = dashboard.get_dept_analysis_detailed()
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        fig = px.scatter(
            dept_detailed,
            x='nb_routes',
            y='taux_mortalite',
            size='nb_accidents',
            color='nb_deces',
            color_continuous_scale='Reds',
            hover_data=['departement', 'route_principale'],
            title="Département: Diversité Routes vs Risque Mortalité",
            labels={
                'nb_routes': 'Nombre de routes différentes',
                'taux_mortalite': 'Taux de mortalité (%)',
                'nb_accidents': "Nombre d'accidents",
                'nb_deces': 'Décès'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top Departements")
        for idx, row in dept_detailed.head(5).iterrows():
            with st.container():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"""
                    **Dept {int(row['departement'])}**  
                    {row['route_principale']} (#{int(row['accidents_route_principale'])})
                    """)
                with col_b:
                    st.metric("Acc.", int(row['nb_accidents']))

# TAB 3: CROISEMENT
with tab3:
    st.markdown("## Croisement Departement x Route")
    
    matrix = dashboard.get_dept_road_matrix()
    
    # Pivot table
    pivot = matrix.pivot_table(
        values='nb_accidents',
        index='adr',
        columns='dept',
        aggfunc='sum',
        fill_value=0
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Heatmap Départements x Routes")
        
        # Limiter à top 10 routes pour lisibilité
        top_routes = matrix.groupby('adr')['nb_accidents'].sum().nlargest(10).index
        pivot_filtered = pivot.loc[top_routes]
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_filtered.values,
            x=pivot_filtered.columns,
            y=pivot_filtered.index,
            colorscale='Reds',
            text=pivot_filtered.values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Accidents")
        ))
        
        fig.update_layout(
            title="Heatmap: Routes (top 10) x Departements",
            xaxis_title="Departement",
            yaxis_title="Route/Adresse",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Vue Tableau")
        display_matrix = matrix.head(20)[['adr', 'dept', 'nb_accidents', 'nb_deces']]
        st.dataframe(display_matrix, use_container_width=True, height=400)

# TAB 4: HOTSPOTS
with tab4:
    st.markdown("## Hotspots - Zones Critiques")
    st.markdown("Routes avec risque de mortalite eleve et accidents frequents")
    
    hotspots = dashboard.get_road_hotspots(threshold=2)
    
    if not hotspots.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart avec gradient danger
            fig = px.bar(
                hotspots,
                x='taux_mortalite',
                y='route',
                orientation='h',
                color='taux_mortalite',
                color_continuous_scale=['yellow', 'orange', 'red'],
                title="Hotspots - Taux de Mortalite",
                labels={
                    'route': 'Route/Adresse',
                    'taux_mortalite': 'Taux mortalite (%)'
                }
            )
            fig.update_traces(text=hotspots['taux_mortalite'].round(1), textposition='outside', texttemplate='%{text:.1f}%')
            fig.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Taux de mortalite (%)",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Routes a Risque Critique")
            for idx, row in hotspots.iterrows():
                severity = "CRITIQUE" if row['taux_mortalite'] > 25 else "ELEVE"
                st.markdown(f"""
                **{severity}** {row['route']}  
                Dept {int(row['departement'])} | {int(row['nb_accidents'])} acc. | {int(row['nb_deces'])} deces  
                Risque: **{row['taux_mortalite']:.1f}%**
                """)
        
        # Recommendations
        st.markdown("---")
        st.markdown("## Recommandations d'Intervention")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_hotspot = hotspots.iloc[0]
            st.warning(f"""
            ### Action Prioritaire
            
            **{top_hotspot['route']}**  
            Departement {int(top_hotspot['departement'])}
            
            - Renforcer controles de vitesse
            - Ameliorer signalisation
            - Etudier geometrie route
            """)
        
        with col2:
            st.info("""
            ### Donnees a Collecter
            
            - Cameras de surveillance
            - Radar de vitesse
            - Capteurs de degradation
            - Conditions meteo
            """)
        
        with col3:
            st.success("""
            ### Actions Recommandees
            
            - Audit de securite
            - Amelioration eclairage
            - Ajuster limitation vitesse
            - Campagne sensibilisation
            """)
    
    else:
        st.info("❌ Aucun hotspot identifié avec les critères actuels")

# ===== DONNÉES BRUTES =====
st.markdown("---")
st.markdown("## 📋 Données Brutes")

with st.expander("Voir toutes les routes (statistiques complètes)"):
    all_roads = dashboard.get_road_statistics()
    st.dataframe(
        all_roads[['route', 'departement', 'nb_accidents', 'nb_deces', 'taux_mortalite']].sort_values(
            'nb_accidents', ascending=False
        ),
        use_container_width=True,
        height=400
    )
