import os
import shutil
import time

from data_generator import generate_referentiel, generate_entreprises, generate_offres
from pipeline.bronze_ingestion import ingest_to_bronze
from pipeline.silver_nlp import charger_referentiel
from pipeline.silver_transform import transformer_bronze_vers_silver
from pipeline.gold_aggregation import construire_gold
from analysis.analyse_marche import lancer_analyse_drh

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(root, "data")
    lake_dir = os.path.join(root, "data_lake")
    
    ref_path = os.path.join(data_dir, "referentiel_competences_it.json")
    ent_path = os.path.join(data_dir, "entreprises_it_maroc.csv")
    raw_path = os.path.join(data_dir, "offres_emploi_it_maroc.json")
    
    bronze_path = os.path.join(lake_dir, "bronze")
    silver_path = os.path.join(lake_dir, "silver")
    gold_path = os.path.join(lake_dir, "gold")

    print("\n" + "#"*70)
    print("DEMARRAGE DU PIPELINE MEXORA RH LAKE")
    print("#"*70)
    
    t0 = time.time()
    
    # 0. Preparation
    os.makedirs(data_dir, exist_ok=True)
    if os.path.exists(lake_dir):
        shutil.rmtree(lake_dir)
    os.makedirs(lake_dir, exist_ok=True)
    
    # 1. Generation des datasets (Etape 0)
    print("\n--- PHASE 0: Generation des datasets ---")
    generate_referentiel(ref_path)
    ent = generate_entreprises(ent_path)
    generate_offres(raw_path, ent)
    
    # 2. Zone Bronze
    print("\n--- PHASE 1: Zone Bronze ---")
    ingest_to_bronze(raw_path, bronze_path)
    
    # 3. Zone Silver
    print("\n--- PHASE 2: Zone Silver (Nettoyage & NLP) ---")
    ref_index = charger_referentiel(ref_path)
    transformer_bronze_vers_silver(bronze_path, silver_path, ref_index)
    
    # 4. Zone Gold
    print("\n--- PHASE 3: Zone Gold (Aggregation) ---")
    construire_gold(silver_path, gold_path)
    
    # 5. Analyse
    print("\n--- PHASE 4: Analyse DRH ---")
    lancer_analyse_drh(gold_path)
    
    t1 = time.time()
    print("\n" + "#"*70)
    print(f"PIPELINE TERMINE EN {t1 - t0:.2f} secondes.")
    print("#"*70)

if __name__ == "__main__":
    main()
