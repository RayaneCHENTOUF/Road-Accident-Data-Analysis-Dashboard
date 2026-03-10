import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

class AccidentsLoader:
    """
    Charge les fichiers nettoyés (data/processed) dans MySQL
    """

    def __init__(self):
        # Charger les variables d'environnement
        load_dotenv()

        # Paramètres MySQL
        db_type = os.getenv("DB_TYPE", "mysql")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "root1")
        db_name = os.getenv("DB_NAME", "accident_etl")

        # Connexion SQLAlchemy
        self.engine = create_engine(
            f"{db_type}+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        )

        # Répertoire des fichiers traités
        self.processed_dir = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))
        self.year = os.getenv("YEARS", "2023")

        # Fichiers à charger
        self.files = {
            "caracteristiques": f"caracteristiques-{self.year}.csv",
            "lieux": f"lieux-{self.year}.csv",
            "vehicules": f"vehicules-{self.year}.csv",
            "usagers": f"usagers-{self.year}.csv",
        }

    def load_file(self, table_name: str, file_path: Path):
        """
        Charge un CSV dans MySQL
        """
        try:
            df = pd.read_csv(file_path, sep=";", encoding="utf-8")
            print(f"🚀 Chargement {table_name} ({len(df)} lignes)")

            df.to_sql(table_name, self.engine, if_exists="replace", index=False)
            print(f"✅ Table {table_name} chargée avec succès dans MySQL")

        except FileNotFoundError:
            print(f"❌ Fichier introuvable: {file_path}")
        except Exception as e:
            print(f"💥 Erreur lors du chargement de {file_path}: {e}")

    def run(self):
        """
        Charge tous les fichiers traités
        """
        for table_name, filename in self.files.items():
            file_path = self.processed_dir / filename
            self.load_file(table_name, file_path)


if __name__ == "__main__":
    loader = AccidentsLoader()
    loader.run()
