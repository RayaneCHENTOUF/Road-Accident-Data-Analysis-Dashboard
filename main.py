"""
Script principal pour telecharger et preparer les donnees
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from extract import AccidentsExtractor
from transform import AccidentsTransformer
from load import AccidentsLoader

def main():
    print("=" * 60)
    print("PIPELINE COMPLET: EXTRACTION -> TRANSFORMATION -> CHARGEMENT")
    print("=" * 60)
    
    # Etape 1: Extraction
    print("\n1️⃣ EXTRACTION des donnees depuis data.gouv.fr...")
    extractor = AccidentsExtractor(year=2023, data_dir="data/raw")
    
    files_to_download = ["caracteristiques", "lieux", "vehicules", "usagers"]
    success_count = 0
    for file_type in files_to_download:
        if extractor.download_file(file_type):
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(files_to_download)} fichier(s) telecharge(s)")
    
    # Etape 2: Transformation
    print("\n2️⃣ TRANSFORMATION des donnees...")
    print("   Nettoyage et standardisation des donnees...")
    transformer = AccidentsTransformer()
    transformer.run()
    
    # Etape 3: Chargement (optionnel)
    print("\n3️⃣ CHARGEMENT en base de donnees (tentative)...")
    try:
        loader = AccidentsLoader()
        loader.run()
        print("\n✅ Donnees chargees en base MySQL")
    except Exception as e:
        print(f"\n⚠️ Chargement en base echoue: {e}")
        print("   Les CSV sont disponibles dans data/processed/")
        print("   Le dashboard utilisera les CSV par defaut")
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLET TERMINE")
    print("=" * 60)
    print("\nPour lancer le dashboard: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
