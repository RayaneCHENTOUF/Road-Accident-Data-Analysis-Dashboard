"""
Module de logique métier pour le dashboard Streamlit
Gestion des requêtes SQL et traitement des données
"""

import pandas as pd
import numpy as np
from sqlalchemy import text
import sys
import os
from datetime import datetime

# Import de la configuration existante
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import config


class DashboardData:
    """Classe pour gérer les données du dashboard"""
    
    def __init__(self):
        self.engine = config.get_database_engine()
        self.connected = self.test_connection()
        self.df_characteristics = None
        self.df_locations = None
        self.df_users = None
        self.df_vehicles = None
        self._load_csv_data()
        
    def _load_csv_data(self):
        """Charge les données CSV depuis le dossier processed"""
        try:
            # Charger caracteristiques
            self.df_characteristics = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/caracteristiques-2023.csv", sep=';', encoding='utf-8')
            # Renommer les colonnes
            self.df_characteristics = self.df_characteristics.rename(columns={
                'num_acc': 'Num_Acc',
                'jour': 'jour',
                'mois': 'mois',
                'an': 'an',
                'hrmn': 'heure',
                'lum': 'lum',
                'dep': 'dept',
                'adr': 'adr',
                'lat': 'lat',
                'long': 'lon'
            })
            # Extraire l'heure de hrmn (format HH:MM)
            self.df_characteristics['heure'] = self.df_characteristics['heure'].str.split(':').str[0].astype(int, errors='ignore')
            # Créer date_acc (premier jour du mois)
            self.df_characteristics['date_acc'] = pd.to_datetime(
                self.df_characteristics['an'].astype(str) + '-' + 
                self.df_characteristics['mois'].astype(str).str.zfill(2) + '-01',
                format='%Y-%m-%d',
                errors='coerce'
            )
            
            # Charger lieux
            self.df_locations = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/lieux-2023.csv", sep=';', encoding='utf-8')
            self.df_locations = self.df_locations.rename(columns={'num_acc': 'Num_Acc', 'vma': 'VitMax'})
            
            # Charger usagers
            self.df_users = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/usagers-2023.csv", sep=';', encoding='utf-8')
            self.df_users = self.df_users.rename(columns={'num_acc': 'Num_Acc'})
            
            # Charger vehicules
            self.df_vehicles = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/vehicules-2023.csv", sep=';', encoding='utf-8')
            self.df_vehicles = self.df_vehicles.rename(columns={'num_acc': 'Num_Acc'})
            
            # Ajouter colonnes derivees
            self._add_derived_columns()
                
        except FileNotFoundError as e:
            print(f"❌ ERREUR: Donnees non trouvees!")
            print(f"   Chemin recherche: {config.PROCESSED_DATA_DIR}/")
            print(f"   Veuillez d'abord executer: python main.py")
            raise e
    
    def _add_derived_columns(self):
        """Ajoute les colonnes derivees calculees"""
        # Compter vehicules par accident
        vehicle_counts = self.df_vehicles.groupby('Num_Acc').size().reset_index(name='nb_vehicules')
        self.df_characteristics = self.df_characteristics.merge(vehicle_counts, on='Num_Acc', how='left')
        self.df_characteristics['nb_vehicules'] = self.df_characteristics['nb_vehicules'].fillna(1).astype(int)
        
        # Compter usagers par accident
        user_counts = self.df_users.groupby('Num_Acc').size().reset_index(name='nb_usagers')
        self.df_characteristics = self.df_characteristics.merge(user_counts, on='Num_Acc', how='left')
        self.df_characteristics['nb_usagers'] = self.df_characteristics['nb_usagers'].fillna(1).astype(int)
        
        # Ajouter gravité (max par accident)
        gravity = self.df_users.groupby('Num_Acc')['grav'].max().reset_index(name='grav')
        self.df_characteristics = self.df_characteristics.merge(gravity, on='Num_Acc', how='left')
        self.df_characteristics['grav'] = self.df_characteristics['grav'].fillna(1).astype(int)
    
    def test_connection(self):
        """Test de connexion à la base"""
        if self.engine is None:
            return False
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Exécute une requête SQL et retourne un DataFrame"""
        if not self.connected:
            return pd.DataFrame()
        try:
            return pd.read_sql(text(query), self.engine, params=params or {})
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")
            return pd.DataFrame()
    
    # ===== METHODS KPI =====
    def get_kpis(self, filters=None):
        """Retourne les KPIs principaux"""
        df = self.df_characteristics.copy()
        
        if filters and 'months' in filters and filters['months']:
            df = df[df['mois'].isin(filters['months'])]
        
        if filters and 'departments' in filters and filters['departments']:
            df = df[df['dept'].isin(filters['departments'])]
        
        kpis = {
            'total_accidents': len(df),
            'total_deaths': int(df[df['grav'] == 3].shape[0]),  # gravité 3 = mortel
            'serious_injured': int(df[df['grav'] == 2].shape[0]),
            'light_injured': int(df[df['grav'] == 1].shape[0]),
            'total_vehicles': int(df['nb_vehicules'].sum()),
            'total_users': int(df['nb_usagers'].sum()),
            'death_rate': (df[df['grav'] == 3].shape[0] / len(df) * 100) if len(df) > 0 else 0
        }
        
        return kpis
    
    # ===== METHODS EVOLUTION =====
    def get_monthly_evolution(self, filters=None):
        """Évolution mensuelle des accidents"""
        df = self.df_characteristics.copy()
        
        monthly = df.groupby('mois').agg({
            'Num_Acc': 'count',
            'nb_usagers': 'sum',
            'grav': lambda x: (x == 3).sum()
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'nb_usagers': 'nb_usagers',
            'grav': 'nb_deces'
        }).reset_index()
        
        return monthly
    
    def get_hourly_distribution(self, filters=None):
        """Distribution par heure"""
        df = self.df_characteristics.copy()
        
        hourly = df.groupby('heure').agg({
            'Num_Acc': 'count'
        }).rename(columns={'Num_Acc': 'nb_accidents'}).reset_index()
        
        return hourly
    
    # ===== METHODS GEOGRAPHICAL =====
    def get_available_departments(self):
        """Récupère les départements disponibles"""
        if self.df_characteristics is not None:
            return sorted(self.df_characteristics['dept'].dropna().unique().tolist())
        return []
    
    def get_available_months(self):
        """Récupère les mois disponibles dans les données"""
        if self.df_characteristics is not None:
            return sorted(self.df_characteristics['mois'].unique().tolist())
        return list(range(1, 13))
    
    def get_top_departments(self, filters=None, limit=10):
        """Top départements par accidents"""
        df = self.df_characteristics.copy()
        
        top_deps = df['dept'].value_counts().head(limit).reset_index()
        top_deps.columns = ['departement', 'nb_accidents']
        top_deps['departement'] = top_deps['departement'].astype(int)
        
        return top_deps
    
    def get_gravity_distribution(self, filters=None):
        """Distribution par gravité"""
        df = self.df_characteristics.copy()
        
        gravity_map = {1: 'Léger', 2: 'Grave', 3: 'Mortel'}
        
        gravity = df.groupby('grav').agg({
            'Num_Acc': 'count'
        }).rename(columns={'Num_Acc': 'nombre'}).reset_index()
        
        gravity['gravite'] = gravity['grav'].map(gravity_map)
        gravity = gravity[['gravite', 'nombre']]
        
        return gravity
    
    # ===== METHODS ANALYSIS =====
    def get_high_risk_hours(self):
        """Heures à risque élevé"""
        df = self.df_characteristics.copy()
        
        hourly_stats = df.groupby('heure').agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum()
        }).rename(columns={'Num_Acc': 'nb_accidents', 'grav': 'nb_deces'})
        
        hourly_stats['taux_mortalite'] = (hourly_stats['nb_deces'] / hourly_stats['nb_accidents'] * 100)
        hourly_stats = hourly_stats.sort_values('taux_mortalite', ascending=False)
        
        return hourly_stats.head(5)
    
    def get_day_analysis(self):
        """Analyse par jour de la semaine"""
        df = self.df_characteristics.copy()
        
        day_map = {4: 'Lundi', 5: 'Mardi', 6: 'Mercredi', 0: 'Jeudi', 1: 'Vendredi', 2: 'Samedi', 3: 'Dimanche'}
        
        daily = df.groupby('jour').agg({
            'Num_Acc': 'count',
            'nb_usagers': 'sum',
            'grav': lambda x: (x == 3).sum()
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'nb_usagers': 'nb_usagers',
            'grav': 'nb_deces'
        }).reset_index()
        
        daily['jour_nom'] = daily['jour'].map(day_map)
        
        return daily
    
    def get_light_conditions_analysis(self):
        """Analyse par conditions d'éclairage"""
        df = self.df_characteristics.copy()
        
        light_map = {1: 'Jour', 2: 'Crépuscule', 3: 'Nuit éclairée', 4: 'Nuit'}
        
        light_stats = df.groupby('lum').agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum()
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'grav': 'nb_deces'
        }).reset_index()
        
        light_stats['condition'] = light_stats['lum'].map(light_map)
        light_stats['taux_mortalite'] = (light_stats['nb_deces'] / light_stats['nb_accidents'] * 100)
        
        return light_stats[['condition', 'nb_accidents', 'nb_deces', 'taux_mortalite']]
    
    def get_vehicle_analysis(self):
        """Analyse par nombre de véhicules impliqués"""
        df = self.df_characteristics.copy()
        
        vehicle_stats = df.groupby('nb_vehicules').agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum(),
            'nb_usagers': 'sum'
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'grav': 'nb_deces'
        }).reset_index()
        
        vehicle_stats['taux_mortalite'] = (vehicle_stats['nb_deces'] / vehicle_stats['nb_accidents'] * 100)
        
        return vehicle_stats
    
    def get_department_statistics(self):
        """Statistiques complètes par département"""
        df = self.df_characteristics.copy()
        
        dept_stats = df.groupby('dept').agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum(),
            'nb_usagers': 'sum'
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'grav': 'nb_deces'
        }).reset_index()
        
        dept_stats['taux_mortalite'] = (dept_stats['nb_deces'] / dept_stats['nb_accidents'] * 100)
        dept_stats = dept_stats.sort_values('nb_accidents', ascending=False)
        
        return dept_stats
    
    # ===== ROUTE & DEPARTMENT ANALYSIS =====
    def get_accidents_by_road(self, limit=15):
        """Top routes par nombre d'accidents"""
        df = self.df_characteristics.copy()
        
        road_stats = df.groupby('adr').agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum(),
            'nb_usagers': 'sum',
            'dept': 'first'
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'grav': 'nb_deces'
        }).reset_index()
        
        road_stats['taux_mortalite'] = (road_stats['nb_deces'] / road_stats['nb_accidents'] * 100)
        road_stats = road_stats.sort_values('nb_accidents', ascending=False)
        
        return road_stats.head(limit)
    
    def get_road_statistics(self):
        """Statistiques complètes par route"""
        df = self.df_characteristics.copy()
        
        road_stats = df.groupby('adr').agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum(),
            'nb_usagers': 'sum',
            'dept': 'first'
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'grav': 'nb_deces',
            'dept': 'departement'
        }).reset_index()
        
        # Renommer adr en route
        road_stats = road_stats.rename(columns={'adr': 'route'})
        
        road_stats['taux_mortalite'] = (road_stats['nb_deces'] / road_stats['nb_accidents'] * 100)
        road_stats = road_stats.sort_values('nb_accidents', ascending=False)
        
        return road_stats
    
    def get_dept_road_matrix(self):
        """Matrice département x route"""
        df = self.df_characteristics.copy()
        
        matrix = df.groupby(['dept', 'adr']).agg({
            'Num_Acc': 'count',
            'grav': lambda x: (x == 3).sum()
        }).rename(columns={
            'Num_Acc': 'nb_accidents',
            'grav': 'nb_deces'
        }).reset_index()
        
        return matrix.sort_values('nb_accidents', ascending=False)
    
    def get_dept_analysis_detailed(self):
        """Analyse détaillée par département avec routes"""
        df = self.df_characteristics.copy()
        
        dept_data = []
        
        for dept in df['dept'].unique():
            dept_df = df[df['dept'] == dept]
            
            # Top 3 routes du département
            top_roads = dept_df['adr'].value_counts().head(3).to_dict()
            
            dept_data.append({
                'departement': dept,
                'nb_accidents': len(dept_df),
                'nb_deces': (dept_df['grav'] == 3).sum(),
                'nb_routes': dept_df['adr'].nunique(),
                'taux_mortalite': (dept_df['grav'] == 3).sum() / len(dept_df) * 100,
                'route_principale': max(top_roads, key=top_roads.get) if top_roads else 'N/A',
                'accidents_route_principale': max(top_roads.values()) if top_roads else 0
            })
        
        return pd.DataFrame(dept_data).sort_values('nb_accidents', ascending=False)
    
    def get_road_hotspots(self, threshold=2):
        """Identification des hotspots (routes avec risque élevé)"""
        road_stats = self.get_road_statistics()
        
        hotspots = road_stats[
            (road_stats['nb_accidents'] >= threshold) & 
            (road_stats['taux_mortalite'] > road_stats['taux_mortalite'].median())
        ].sort_values('taux_mortalite', ascending=False)
        
        return hotspots
    
    # ===== DATA QUALITY =====
    def get_data_quality_report(self):
        """Rapport de qualité des données"""
        report = {
            'total_accidents': len(self.df_characteristics),
            'date_range': f"{self.df_characteristics['date_acc'].min().date()} à {self.df_characteristics['date_acc'].max().date()}",
            'departments_count': self.df_characteristics['dept'].nunique(),
            'missing_values': self.df_characteristics.isnull().sum().to_dict(),
            'data_types': self.df_characteristics.dtypes.to_dict()
        }
        
        return report
    
    def get_summary_stats(self):
        """Statistiques résumées"""
        df = self.df_characteristics
        
        stats = {
            'Total accidents': len(df),
            'Total décès': int(df[df['grav'] == 3].shape[0]),
            'Total usagers touchés': int(df['nb_usagers'].sum()),
            'Total véhicules impliqués': int(df['nb_vehicules'].sum()),
            'Accidents par mois (moyenne)': f"{len(df) / df['mois'].nunique():.1f}",
            'Accidents par département (moyenne)': f"{len(df) / df['dept'].nunique():.1f}",
            'Taux de mortalité': f"{(df[df['grav'] == 3].shape[0] / len(df) * 100):.2f}%"
        }
        
        return stats
