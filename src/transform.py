import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

class AccidentsTransformer:
    """
    Transforme les données d'accidents : nettoyage et sauvegarde en 'processed'
    """

    def __init__(self):
        # Charger les variables d'environnement
        load_dotenv()

        self.raw_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
        self.processed_dir = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.year = os.getenv("YEARS", "2023")

        self.files = {
            "caracteristiques": f"caracteristiques-{self.year}.csv",
            "lieux": f"lieux-{self.year}.csv",
            "vehicules": f"vehicules-{self.year}.csv",
            "usagers": f"usagers-{self.year}.csv",
        }

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoyage simple : colonnes, types, suppression valeurs manquantes
        """
        # Colonnes standardisées
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Conversion dates si possible
        for col in df.columns:
            if "date" in col or "jour" in col:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    pass

        # Supprimer lignes vides
        df = df.dropna(how="all")

        return df

    def run(self):
        for name, filename in self.files.items():
            input_path = self.raw_dir / filename
            output_path = self.processed_dir / filename

            print(f"\n📂 Traitement {input_path} -> {output_path}")

            try:
                df = pd.read_csv(input_path, sep=";", encoding="utf-8")
                print(f"  → {df.shape[0]} lignes, {df.shape[1]} colonnes avant nettoyage")

                df = self.clean_dataframe(df)

                print(f"  → {df.shape[0]} lignes, {df.shape[1]} colonnes après nettoyage")

                # Sauvegarde en processed
                df.to_csv(output_path, sep=";", index=False, encoding="utf-8")
                print(f"✅ Fichier nettoyé sauvegardé dans {output_path}")

            except FileNotFoundError:
                print(f"❌ Fichier introuvable: {input_path}")
            except Exception as e:
                print(f"💥 Erreur lors du traitement de {input_path}: {e}")


if __name__ == "__main__":
    transformer = AccidentsTransformer()
    transformer.run()
