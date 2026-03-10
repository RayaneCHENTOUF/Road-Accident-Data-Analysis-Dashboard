import requests
import os
from pathlib import Path
import pandas as pd
from typing import Dict, List
import time

class AccidentsExtractor:
    """
    Extracteur de données d'accidents de la route depuis data.gouv.fr
    """
    
    def __init__(self, year: int = 2023, data_dir: str = "data/raw",  limit_rows: int = None):
        self.year = year
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.limit_rows = limit_rows

        # URLs de base pour data.gouv.fr
        self.base_url = "https://www.data.gouv.fr/fr/datasets/r/"
        
        # Mapping des fichiers et leurs IDs (à ajuster selon les vrais IDs)
        self.file_mapping = {
            "caracteristiques": {
                "filename": f"caracteristiques-{year}.csv",
                "resource_id": "104dbb32-704f-4e99-a71e-43563cb604f2"  # À remplacer par le vrai ID
            },
            "lieux": {
                "filename": f"lieux-{year}.csv", 
                "resource_id": "8bef19bf-a5e4-46b3-b5f9-a145da4686bc"
            },
            "vehicules": {
                "filename": f"vehicules-{year}.csv",
                "resource_id": "146a42f5-19f0-4b3e-a887-5cd8fbef057b"
            },
            "usagers": {
                "filename": f"usagers-{year}.csv",
                "resource_id": "68848e2a-28dd-4efc-9d5f-d512f7dbe66f"
            }
        }
    
    def download_file(self, file_type: str, retry_count: int = 3) -> bool:
        """
        Télécharge un fichier spécifique
        """
        file_info = self.file_mapping[file_type]
        filename = file_info["filename"]
        file_path = self.data_dir / filename
        
        # Si le fichier existe déjà, on le garde
        if file_path.exists():
            print(f"✅ {filename} existe déjà, pas de téléchargement")
            return True
            
        # Construction de l'URL directe
        url = f"{self.base_url}{file_info['resource_id']}"
        
        for attempt in range(retry_count):
            try:
                print(f"📥 Téléchargement de {filename} (tentative {attempt + 1})")
                
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Sauvegarde du fichier
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Vérification du téléchargement
                if file_path.exists() and file_path.stat().st_size > 0:
                    print(f"✅ {filename} téléchargé avec succès ({file_path.stat().st_size} bytes)")
                    return True
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur lors du téléchargement de {filename}: {e}")
                if attempt < retry_count - 1:
                    print(f"⏳ Attente de 5 secondes avant nouvelle tentative...")
                    time.sleep(5)
                    
        print(f"💥 Échec du téléchargement de {filename} après {retry_count} tentatives")
        return False
    
    def verify_files(self) -> Dict[str, Dict]:
        """
        Vérifie les fichiers téléchargés et donne des infos
        """
        verification_results = {}
        
        for file_type, file_info in self.file_mapping.items():
            filename = file_info["filename"]
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                verification_results[file_type] = {"status": "missing", "error": "Fichier non trouvé"}
                continue
                
            try:
                # MODIFICATION: Lecture adaptée à la taille du fichier
                df = pd.read_csv(file_path, sep=';', encoding='utf-8')
                
                # Prendre un échantillon pour l'aperçu (max 5 lignes)
                sample_rows = min(5, len(df))
                df_sample = df.head(sample_rows)
                
                verification_results[file_type] = {
                    "status": "ok",
                    "file_size": file_path.stat().st_size,
                    "total_rows": len(df),  # NOUVEAU: nombre total de lignes
                    "columns": list(df.columns),
                    "sample_shape": df_sample.shape
                }
                
            except Exception as e:
                verification_results[file_type] = {
                    "status": "error", 
                    "error": str(e)
                }
                
        return verification_results

    # MODIFICATION 4: Modifier download_all_files pour inclure la limitation
    def download_all_files(self) -> Dict[str, bool]:
        """
        Télécharge tous les fichiers de l'année et les limite si demandé
        """
        results = {}
        
        print(f"🚀 Début du téléchargement des fichiers pour {self.year}")
        print(f"📁 Répertoire de destination: {self.data_dir.absolute()}")
        if self.limit_rows:
            print(f"✂️ Limitation activée: {self.limit_rows} lignes par fichier")
        
        # Étape 1: Téléchargement
        for file_type in self.file_mapping.keys():
            results[file_type] = self.download_file(file_type)
            time.sleep(1)  # Pause entre les téléchargements
        
        # Étape 2: Limitation (NOUVEAU)
        if self.limit_rows and any(results.values()):
            print(f"\n✂️ LIMITATION DES FICHIERS À {self.limit_rows} LIGNES...")
            limit_results = self.limit_files_to_rows()
            
            # Combiner les résultats
            for file_type in results:
                if results[file_type] and not limit_results.get(file_type, False):
                    print(f"⚠️ {file_type}: Téléchargé mais limitation échouée")
            
        return results
    
    def limit_files_to_rows(self) -> Dict[str, bool]:
        """
        NOUVELLE FONCTION: Limite chaque fichier CSV à N lignes après téléchargement
        """
        if not self.limit_rows:
            print("🔄 Pas de limitation demandée")
            return {}
            
        print(f"✂️ Limitation des fichiers à {self.limit_rows} lignes...")
        results = {}
        
        for file_type, file_info in self.file_mapping.items():
            filename = file_info["filename"]
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                print(f"⚠️ {filename} n'existe pas, impossible de limiter")
                results[file_type] = False
                continue
                
            try:
                # Lire le fichier complet
                print(f"📖 Lecture de {filename}...")
                df = pd.read_csv(file_path, sep=';', encoding='utf-8')
                original_rows = len(df)
                
                # Limiter aux N premières lignes
                df_limited = df.head(self.limit_rows)
                limited_rows = len(df_limited)
                
                # Sauvegarder le fichier limité
                df_limited.to_csv(file_path, sep=';', index=False, encoding='utf-8')
                
                print(f"✂️ {filename}: {original_rows} → {limited_rows} lignes")
                results[file_type] = True
                
            except Exception as e:
                print(f"❌ Erreur limitation {filename}: {e}")
                results[file_type] = False
                
        return results

    
    def get_files_info(self) -> Dict[str, str]:
        """
        Retourne les chemins des fichiers téléchargés
        """
        files_paths = {}
        for file_type, file_info in self.file_mapping.items():
            file_path = self.data_dir / file_info["filename"]
            if file_path.exists():
                files_paths[file_type] = str(file_path)
        return files_paths


# Script principal pour tester
if __name__ == "__main__":
    # Créer l'extracteur
    extractor = AccidentsExtractor(year=2023, limit_rows=100)
    
    # Télécharger les fichiers
    download_results = extractor.download_all_files()
    
    # Afficher les résultats
    print("\n📊 RÉSULTATS DU TÉLÉCHARGEMENT:")
    for file_type, success in download_results.items():
        status = "✅ Succès" if success else "❌ Échec"
        print(f"{file_type}: {status}")
    
    # Vérifier les fichiers
    print("\n🔍 VÉRIFICATION DES FICHIERS:")
    verification = extractor.verify_files()
    
    for file_type, info in verification.items():
        print(f"\n{file_type}:")
        if info["status"] == "ok":
            print(f"  ✅ Taille: {info['file_size']} bytes")
            print(f"  📊 Lignes: {info['total_rows']}")
            print(f"  📋 Colonnes: {len(info['columns'])}")
            print(f"  📊 Aperçu: {info['columns'][:3]}...")
        else:
            print(f"  ❌ Erreur: {info.get('error', 'Inconnu')}")