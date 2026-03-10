import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

class AccidentsTableCreator:
    """
    Crée les tables MySQL pour les données d'accidents
    """
    
    def __init__(self):
        load_dotenv()
        
        # Paramètres de connexion
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_user = os.getenv("DB_USER", "root1")
        db_password = os.getenv("DB_PASSWORD", "dbl2025")
        db_name = os.getenv("DB_NAME", "accident_etl")
        
        # Créer la connexion
        try:
            if db_password:
                connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            else:
                connection_string = f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}"
            
            self.engine = create_engine(connection_string)
            print("✅ Connexion MySQL établie")
        except Exception as e:
            print(f"❌ Erreur connexion MySQL: {e}")
            exit(1)
    
    def create_database_if_not_exists(self):
        """
        Crée la base de données si elle n'existe pas
        """
        try:
            db_name = os.getenv("DB_NAME", "accident_etl")
            
            # Connexion sans spécifier la base
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "3306")
            db_user = os.getenv("DB_USER", "root1")
            db_password = os.getenv("DB_PASSWORD", "dbl2025")
            
            if db_password:
                temp_engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}")
            else:
                temp_engine = create_engine(f"mysql+pymysql://{db_user}@{db_host}:{db_port}")
            
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
                print(f"✅ Base de données '{db_name}' créée/vérifiée")
                
        except Exception as e:
            print(f"⚠️ Erreur création base: {e}")
    
    def get_table_structures(self):
        """
        Définit la structure des tables basée sur les vraies données d'accidents
        """
        return {
            "caracteristiques": """
                CREATE TABLE IF NOT EXISTS caracteristiques (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    num_acc VARCHAR(12) UNIQUE NOT NULL,
                    jour INT,
                    mois INT,
                    an INT,
                    hrmn VARCHAR(4),
                    lum VARCHAR(50),
                    dep VARCHAR(3),
                    com VARCHAR(3), 
                    agg INT,
                    int_acc INT,
                    atm VARCHAR(50),
                    col INT,
                    adr TEXT,
                    gps CHAR(1),
                    lat DECIMAL(10, 8),
                    long_acc DECIMAL(11, 8),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            "lieux": """
                CREATE TABLE IF NOT EXISTS lieux (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    num_acc VARCHAR(12) NOT NULL,
                    catr VARCHAR(50),
                    voie VARCHAR(100),
                    v1 INT,
                    v2 VARCHAR(10),
                    circ INT,
                    nbv INT,
                    pr INT,
                    pr1 VARCHAR(10),
                    vosp INT,
                    prof VARCHAR(50),
                    plan VARCHAR(50),
                    lartpc VARCHAR(10),
                    larrout VARCHAR(10),
                    surf VARCHAR(50),
                    infra INT,
                    situ INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (num_acc) REFERENCES caracteristiques(num_acc)
                )
            """,
            
            "vehicules": """
                CREATE TABLE IF NOT EXISTS vehicules (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    num_acc VARCHAR(12) NOT NULL,
                    id_vehicule VARCHAR(10),
                    num_veh CHAR(1),
                    senc INT,
                    catv VARCHAR(50),
                    obs INT,
                    obsm INT,
                    choc INT,
                    manv INT,
                    motor VARCHAR(50),
                    occutc INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (num_acc) REFERENCES caracteristiques(num_acc)
                )
            """,
            
            "usagers": """
                CREATE TABLE IF NOT EXISTS usagers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    num_acc VARCHAR(12) NOT NULL,
                    id_vehicule VARCHAR(10),
                    num_veh CHAR(1),
                    place INT,
                    catu VARCHAR(50),
                    grav VARCHAR(50),
                    sexe INT,
                    an_nais INT,
                    trajet VARCHAR(50),
                    secu1 INT,
                    locp INT,
                    actp VARCHAR(50),
                    etatp INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (num_acc) REFERENCES caracteristiques(num_acc)
                )
            """
        }
    
    def analyze_existing_data(self):
        """
        Analyse les fichiers CSV pour adapter la structure des tables
        """
        print("🔍 ANALYSE DES FICHIERS CSV EXISTANTS...")
        
        processed_dir = Path("data/processed")
        year = os.getenv("YEARS", "2023")
        
        files_to_check = [
            f"caracteristiques-{year}.csv",
            f"lieux-{year}.csv", 
            f"vehicules-{year}.csv",
            f"usagers-{year}.csv"
        ]
        
        for filename in files_to_check:
            file_path = processed_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path, sep=';', encoding='utf-8')
                    print(f"\n📊 {filename}:")
                    print(f"  - {len(df)} lignes, {len(df.columns)} colonnes")
                    print(f"  - Colonnes: {list(df.columns)}")
                    
                    # Vérifier les types de données pour quelques colonnes clés
                    if 'num_acc' in df.columns:
                        max_len = df['num_acc'].astype(str).str.len().max()
                        print(f"  - num_acc max length: {max_len}")
                        
                except Exception as e:
                    print(f"  ❌ Erreur lecture {filename}: {e}")
            else:
                print(f"⚠️ {filename} non trouvé")
    
    def create_all_tables(self):
        """
        Crée toutes les tables
        """
        print("\n🏗️ CRÉATION DES TABLES...")
        
        table_structures = self.get_table_structures()
        
        with self.engine.connect() as conn:
            # Désactiver les contraintes temporairement pour éviter les erreurs d'ordre
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            for table_name, sql in table_structures.items():
                try:
                    print(f"🏗️ Création table {table_name}...")
                    conn.execute(text(sql))
                    print(f"✅ Table {table_name} créée/vérifiée")
                except Exception as e:
                    print(f"❌ Erreur création {table_name}: {e}")
            
            # Réactiver les contraintes
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            conn.commit()
    
    def verify_tables(self):
        """
        Vérifie que toutes les tables ont été créées
        """
        print("\n🔍 VÉRIFICATION DES TABLES...")
        
        with self.engine.connect() as conn:
            # Lister toutes les tables
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['caracteristiques', 'lieux', 'vehicules', 'usagers']
            
            print(f"📋 Tables trouvées: {tables}")
            
            for table in expected_tables:
                if table in tables:
                    # Vérifier la structure
                    result = conn.execute(text(f"DESCRIBE {table}"))
                    columns = [row[0] for row in result.fetchall()]
                    print(f"✅ {table}: {len(columns)} colonnes -> {columns[:3]}...")
                else:
                    print(f"❌ {table}: MANQUANTE")
    
    def run(self):
        """
        Lance tout le processus de création
        """
        print("🚀 CRÉATION DES TABLES MYSQL POUR LES ACCIDENTS")
        
        # Étape 1: Créer la base si besoin
        self.create_database_if_not_exists()
        
        # Étape 2: Analyser les données existantes
        self.analyze_existing_data()
        
        # Étape 3: Créer les tables
        self.create_all_tables()
        
        # Étape 4: Vérifier
        self.verify_tables()
        
        print("\n✅ CRÉATION DES TABLES TERMINÉE !")
        print("🎯 Vous pouvez maintenant lancer le loader !")

if __name__ == "__main__":
    creator = AccidentsTableCreator()
    creator.run()