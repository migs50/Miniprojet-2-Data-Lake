import duckdb
import os

def lancer_analyse_drh(gold_path):
    print("\n" + "="*70)
    print("ANALYSE DU MARCHE DE L'EMPLOI IT (MEXORA RH)")
    print("="*70)
    
    con = duckdb.connect()
    
    p_comp = os.path.join(gold_path, "top_competences.parquet").replace("\\", "/")
    p_sal = os.path.join(gold_path, "salaires_par_profil.parquet").replace("\\", "/")
    p_ville = os.path.join(gold_path, "offres_par_ville.parquet").replace("\\", "/")
    p_ent = os.path.join(gold_path, "entreprises_recruteurs.parquet").replace("\\", "/")
    
    print("\nQ1. Quelles competences sont les plus demandees ?")
    res1 = con.execute(f"SELECT competence, nb_offres FROM read_parquet('{p_comp}') ORDER BY nb_offres DESC LIMIT 5").df()
    print(res1.to_string(index=False))
    
    print("\nQ2. Quel est le salaire median a Tanger pour un Data Engineer ?")
    res2 = con.execute(f"SELECT ville_clean, categorie_poste, ROUND(AVG(salaire_median_mad), 0) as salaire_moyen FROM read_parquet('{p_sal}') WHERE LOWER(ville_clean) = 'tanger' AND categorie_poste = 'Data Engineer' GROUP BY ville_clean, categorie_poste").df()
    if res2.empty:
        print(" -> Pas assez de donnees pour Data Engineer a Tanger dans ce jeu.")
    else:
        print(res2.to_string(index=False))
        
    print("\nQ3. Est-ce que les entreprises recrutent plutot en CDI ou en freelance ?")
    res3 = con.execute(f"SELECT type_contrat, SUM(nb_offres) AS nb_total FROM read_parquet('{p_ville}') GROUP BY type_contrat ORDER BY nb_total DESC").df()
    print(res3.to_string(index=False))
        
    print("\nQ4. Qui sont nos concurrents sur le marche du talent ? (Top 5 recruteurs)")
    res4 = con.execute(f"SELECT entreprise, nb_offres_totales FROM read_parquet('{p_ent}') ORDER BY nb_offres_totales DESC LIMIT 5").df()
    print(res4.to_string(index=False))
    con.close()
