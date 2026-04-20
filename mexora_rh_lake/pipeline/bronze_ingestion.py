import json
import os
import shutil
from datetime import datetime

def ingest_to_bronze(raw_file_path, bronze_path):
    """
    Ingere les donnees JSON dans la zone Bronze.
    Partitionnement dynamique: bronze/<source>/<YYYY_MM>/offres_raw.json
    """
    print(f"\n[BRONZE] Debut de l'ingestion depuis {raw_file_path}...")
    
    # Lecture des donnees brutes
    with open(raw_file_path, 'r', encoding='utf-8') as f:
        offres = json.load(f)
        
    partitions = {}

    for offre in offres:
        source = offre.get('source', 'inconnue')
        date_pub = offre.get('date_publication', '')
        
        annee_mois = "inconnue"
        if date_pub:
            # Essayer de parser la date pour partitionnement
            try:
                dt = datetime.strptime(date_pub, "%Y-%m-%d")
                annee_mois = dt.strftime("%Y_%m")
            except ValueError:
                try:
                    dt = datetime.strptime(date_pub, "%d/%m/%Y")
                    annee_mois = dt.strftime("%Y_%m")
                except ValueError:
                    pass
                    
        cle_partition = (source, annee_mois)
        if cle_partition not in partitions:
            partitions[cle_partition] = []
            
        partitions[cle_partition].append(offre)
        
    # Ecriture des partitions
    for (source, annee_mois), donnees in partitions.items():
        partition_dir = os.path.join(bronze_path, source, annee_mois)
        os.makedirs(partition_dir, exist_ok=True)
        
        file_path = os.path.join(partition_dir, "offres_raw.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=2, ensure_ascii=False)
            
    print(f"[OK] Ingestion terminee : {len(offres)} offres reparties dans {len(partitions)} partitions.")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    raw_json = os.path.join(project_root, "data", "offres_emploi_it_maroc.json")
    bronze = os.path.join(project_root, "data_lake", "bronze")
    
    if os.path.exists(bronze):
        shutil.rmtree(bronze)
        
    ingest_to_bronze(raw_json, bronze)
