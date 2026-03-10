import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Charger le fichier .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class Config:
    """Configuration centralisée pour le projet ETL Accidents"""
    
    # === BASE DE DONNÉES MYSQL ===
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root1')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'dbl2025')
    DB_NAME = os.getenv('DB_NAME', 'accident_etl')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # URL de connexion pour SQLAlchemy
    @property
    def database_url(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # === DATA GOUV ===
    DATA_GOUV_BASE_URL = os.getenv('DATA_GOUV_BASE_URL', 'https://www.data.gouv.fr/fr/datasets/r/')
    
    # === DOSSIERS ===
    RAW_DATA_DIR = Path(os.getenv('RAW_DATA_DIR', 'data/raw'))
    PROCESSED_DATA_DIR = Path(os.getenv('PROCESSED_DATA_DIR', 'data/processed'))
    
    # Créer les dossiers s'ils n'existent pas
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # === ANNÉES À TRAITER ===
    YEARS = [int(y.strip()) for y in os.getenv('YEARS', '2023').split(',')]
    
    # === FICHIERS D'ACCIDENTS PAR ANNÉE ===
    ACCIDENT_FILES = ['caracteristiques', 'lieux', 'vehicules', 'usagers']
    
    def get_database_engine(self):
        """Créé et retourne l'engine SQLAlchemy pour MySQL"""
        try:
            engine = create_engine(self.database_url, echo=False)
            return engine
        except Exception as e:
            print(f"❌ Erreur de connexion à MySQL: {e}")
            return None
    
    def test_connection(self):
        """Test de connexion à la base MySQL"""
        engine = self.get_database_engine()
        if engine is None:
            return False
            
        try:
            from sqlalchemy import text
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                print("✅ Connexion MySQL réussie !")
                return True
        except Exception as e:
            print(f"❌ Erreur de test de connexion: {e}")
            return False

# Instance globale de configuration
config = Config()

# Test rapide si ce fichier est exécuté directement
if __name__ == "__main__":
    print("🧪 TEST DE CONFIGURATION")
    print("=" * 40)
    print(f"Base de données: {config.DB_TYPE}")
    print(f"Host: {config.DB_HOST}:{config.DB_PORT}")
    print(f"Database: {config.DB_NAME}")
    print(f"User: {config.DB_USER}")
    print(f"Années: {config.YEARS}")
    print(f"Dossier données: {config.RAW_DATA_DIR}")
    
    # Test de connexion
    print("\n🔌 Test de connexion...")
    config.test_connection()
