import os
import glob
import json
import pandas as pd
from pipeline.utils import normaliser_ville, normaliser_titre, parser_salaire, parser_experience, parser_date, valider_dates
from pipeline.silver_nlp import extraire_competences_brut, extraire_competences_nlp, construire_table_competences

def transformer_bronze_vers_silver(bronze_path, silver_path, ref_index):
    print("\n[SILVER] Transformation Bronze -> Silver...")
    tous_json = glob.glob(os.path.join(bronze_path, "**", "**", "offres_raw.json"))
    lignes = []
    for chemin in tous_json:
        with open(chemin, "r", encoding="utf-8") as f:
            lignes.extend(json.load(f))
    df = pd.DataFrame(lignes)
    
    # Transformations
    df["ville_clean"] = df["ville"].apply(normaliser_ville)
    df["categorie_poste"] = df["titre_poste"].apply(normaliser_titre)
    
    salaires = df["salaire_brut"].apply(parser_salaire)
    df["salaire_min_mad"] = salaires.apply(lambda x: x[0])
    df["salaire_max_mad"] = salaires.apply(lambda x: x[1])
    df["salaire_median_mad"] = df.apply(lambda r: (r["salaire_min_mad"]+r["salaire_max_mad"])/2 if pd.notna(r["salaire_min_mad"]) else None, axis=1)
    df["salaire_disponible"] = df["salaire_min_mad"].notna()
    
    exp = df["experience_requise"].apply(parser_experience)
    df["experience_min_ans"] = exp.apply(lambda x: x[0])
    df["experience_max_ans"] = exp.apply(lambda x: x[1])
    
    df["date_pub_dt"] = df["date_publication"].apply(parser_date)
    df["date_exp_dt"] = df["date_expiration"].apply(parser_date)
    df["dates_coherentes"] = df.apply(lambda r: valider_dates(r["date_pub_dt"], r["date_exp_dt"]), axis=1)
    
    df["competences_liste"] = df["competences_brut"].apply(extraire_competences_brut)
    df["competences_nlp"] = df["description"].apply(lambda t: extraire_competences_nlp(t, ref_index))
    
    # Table Silver 1: Offres
    colonnes_ok = [c for c in df.columns if c not in ["date_pub_dt", "date_exp_dt", "competences_liste", "competences_nlp", "langue_requise"]]
    df_offres = df[colonnes_ok].copy()
    
    for c in ["salaire_disponible", "dates_coherentes"]:
        df_offres[c] = df_offres[c].astype(int)
        
    p1 = os.path.join(silver_path, "offres_clean", "offres_clean.parquet")
    os.makedirs(os.path.dirname(p1), exist_ok=True)
    df_offres.to_parquet(p1, index=False, engine="pyarrow")
    
    # Table Silver 2: Competences relationnelle
    df_comp = construire_table_competences(df)
    for c in ["famille", "competence_canonique"]:
        df_comp[c] = df_comp[c].astype(str)
        
    p2 = os.path.join(silver_path, "competences_extraites", "competences.parquet")
    os.makedirs(os.path.dirname(p2), exist_ok=True)
    df_comp.to_parquet(p2, index=False, engine="pyarrow")
    
    print(f"[OK] Silver termin :\n  - Offres = {len(df_offres)} lignes\n  - Competences = {len(df_comp)} lignes")
