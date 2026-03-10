# Dashboard Sécurité Routière - Accidents 2023

Un projet personnel pour apprendre l'ETL, l'analyse de données et la création de dashboards interactifs avec Python.

## Description

Ce dashboard analyse les données d'accidents routiers de 2023 (source: BAAC). L'objectif est d'explorer les données, identifier les patterns et créer des visualisations pour mieux comprendre les risques routiers.

## Fonctionnalités

**Page d'accueil:**

- KPIs principaux (nombre d'accidents, décès, blessures)
- Évolution mensuelle des accidents
- Distribution par gravité
- Analyse horaire des accidents
- Conditions d'éclairage et impact
- Statistiques par département
- Analyse multi-véhicules

**Pages additionnelles:**

- Analyses avancées (journalière, véhicules, éclairage)
- Analyse des heures dangereuses avec recommandations
- Analyse détaillée routes et départements
- Identification des hotspots (zones à risque élevé)

## Installation

### Prérequis

- Python 3.10+
- MySQL 5.7+ (optionnel, l'app fonctionne avec CSV)
- Git

### Étapes

1. Cloner le projet

```bash
git clone https://github.com/votre-username/accident_etl.git
cd accident_etl
```

2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances

```bash
pip install -r requirements.txt
```

4. Configurer la base de données (optionnel)

```bash
cp config/.env.example config/.env
# Éditer config/.env avec vos credentials
```

5. Lancer le dashboard

```bash
streamlit run streamlit_app.py
```

L'app s'ouvre sur http://localhost:8501

## Structure du Projet

```
accident_etl/
├── streamlit_app.py          # App principale
├── requirements.txt          # Dépendances
│
├── pages/                    # Pages Streamlit
│   ├── 1_analyses_avancees.py
│   ├── 2_heures_dangereuses.py
│   └── 3_routes_departements.py
│
├── src/                      # Code métier
│   ├── dashboard.py          # Logique d'analyse
│   └── __init__.py
│
├── config/                   # Configuration
│   ├── config.py
│   ├── .env.example
│   └── __init__.py
│
└── data/                     # Données
    ├── raw/
    └── processed/
        ├── caracteristiques-2023.csv
        ├── lieux-2023.csv
        ├── usagers-2023.csv
        └── vehicules-2023.csv
```

## Technologies Utilisées

- **Python 3.13** - Langage principal
- **Streamlit** - Framework web
- **Pandas/NumPy** - Manipulation de données
- **Plotly** - Visualisations interactives
- **SQLAlchemy** - ORM pour base de données
- **MySQL** - Base de données (optionnel)

## Données

Les données proviennent de data.gouv.fr - BAAC 2023 (Fichiers des Accidents de la Circulation).

Les fichiers CSV incluent:

- Caractéristiques des accidents (date, heure, gravité)
- Lieux (département, route)
- Usagers impliqués
- Véhicules

## Apprentissages

Ce projet m'a permis de:

- Manipuler et nettoyer des données avec Pandas
- Créer une architecture modulaire en Python
- Utiliser Plotly pour des visualisations interactives
- Développer une interface avec Streamlit
- Gérer une base de données MySQL
- Appliquer des concepts d'ETL simples

## Améliorations Futures

- Ajouter des prédictions avec des modèles ML
- Créer une heatmap géographique
- Ajouter plus de filtres interactifs
- Export PDF des rapports
- Tests unitaires

## Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue.

## Licence

MIT License
