import duckdb
import os

def creer_connexion(silver_path):
    con = duckdb.connect()
    p_offres = os.path.join(silver_path, "offres_clean", "offres_clean.parquet").replace("\\", "/")
    p_comp = os.path.join(silver_path, "competences_extraites", "competences.parquet").replace("\\", "/")
    con.execute(f"CREATE VIEW offres AS SELECT * FROM read_parquet('{p_offres}')")
    con.execute(f"CREATE VIEW competences AS SELECT * FROM read_parquet('{p_comp}')")
    return con

def construire_gold(silver_path, gold_path):
    print("\n[GOLD] Calcul des aggregats et stockage via DuckDB...")
    os.makedirs(gold_path, exist_ok=True)
    con = creer_connexion(silver_path)
    
    # 1. Top Competences
    sql_comp = """
        SELECT competence_canonique AS competence, famille,
               COUNT(DISTINCT id_offre) AS nb_offres,
               STRING_AGG(DISTINCT categorie_poste, ', ') AS profils_demandeurs
        FROM competences
        WHERE competence_canonique IS NOT NULL AND competence_canonique != 'None'
        GROUP BY competence_canonique, famille
        ORDER BY nb_offres DESC
    """
    df_top = con.execute(sql_comp).df()
    for col in df_top.select_dtypes(include=["object"]).columns:
        df_top[col] = df_top[col].apply(lambda x: str(x) if x else "")
    df_top.to_parquet(os.path.join(gold_path, "top_competences.parquet"))
    
    # 2. Salaires par Profil
    sql_sal = """
        SELECT categorie_poste, ville_clean, type_contrat,
               COUNT(*) AS nb_offres,
               ROUND(MEDIAN(salaire_median_mad), 0) AS salaire_median_mad,
               MIN(salaire_min_mad) AS salaire_min_mad, MAX(salaire_max_mad) AS salaire_max_mad
        FROM offres
        WHERE salaire_disponible = 1 AND salaire_median_mad BETWEEN 3000 AND 100000
          AND categorie_poste != 'Autre'
        GROUP BY categorie_poste, ville_clean, type_contrat
        HAVING nb_offres >= 2
    """
    df_sal = con.execute(sql_sal).df()
    df_sal.to_parquet(os.path.join(gold_path, "salaires_par_profil.parquet"))
    
    # 3. Offres par ville
    sql_ville = """
        SELECT ville_clean, categorie_poste, type_contrat,
               COUNT(*) as nb_offres, ROUND(MEDIAN(salaire_median_mad), 0) as salaire_median
        FROM offres
        GROUP BY ville_clean, categorie_poste, type_contrat
    """
    df_ville = con.execute(sql_ville).df()
    df_ville.to_parquet(os.path.join(gold_path, "offres_par_ville.parquet"))
    
    # 4. Entreprises recruteurs
    sql_ent = """
        SELECT entreprise, ville_clean,
               COUNT(*) AS nb_offres_totales,
               COUNT(DISTINCT categorie_poste) AS profils_differents,
               ROUND(MEDIAN(CASE WHEN salaire_disponible = 1 THEN salaire_median_mad END), 0) AS med_salaire
        FROM offres
        GROUP BY entreprise, ville_clean
    """
    df_ent = con.execute(sql_ent).df()
    df_ent.to_parquet(os.path.join(gold_path, "entreprises_recruteurs.parquet"))
    
    # 5. Tendances
    sql_tend = """
        SELECT source, type_contrat, COUNT(*) as nb_total
        FROM offres
        GROUP BY source, type_contrat
    """
    df_tend = con.execute(sql_tend).df()
    df_tend.to_parquet(os.path.join(gold_path, "tendances_mensuelles.parquet"))
    
    print("[OK] Les 5 tables Gold ont ete generees avec succes.")
    con.close()
