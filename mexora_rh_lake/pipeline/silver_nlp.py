import json
import pandas as pd
import re

def charger_referentiel(ref_path):
    with open(ref_path, "r", encoding="utf-8") as f:
        ref = json.load(f)
    index = {}
    for famille, skills in ref["familles"].items():
        for canon, variantes in skills.items():
            for v in variantes:
                index[v.lower()] = (famille, canon)
    return index

def extraire_competences_brut(comp_str):
    if not comp_str or pd.isna(comp_str): return []
    s = re.sub(r'[/;\|\n\t]', ',', str(comp_str))
    s = re.sub(r'\s+-\s+', ',', s)
    return [p.strip() for p in s.split(',') if len(p.strip()) > 1]

def extraire_competences_nlp(texte, referentiel_index):
    """Cherche via expressions regulieres les competences referencees dans le texte."""
    if not texte or pd.isna(texte): return []
    texte_lower = str(texte).lower()
    trouvees = set()
    
    # Les competences formees de plusieurs mots doivent etre flitrees en premier
    for var in sorted(referentiel_index.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(var) + r'\b', texte_lower):
            trouvees.add(referentiel_index[var])
            
    return [{"famille": f, "competence": c} for f, c in sorted(trouvees)]

def construire_table_competences(df_silver):
    """Cree la table d'association Id_Offre <-> Competence."""
    lignes = []
    for _, row in df_silver.iterrows():
        # Depuis l'extraction brute
        for comp in row.get("competences_liste", []):
            lignes.append({
                "id_offre": row["id_offre"],
                "ville_clean": row["ville_clean"],
                "categorie_poste": row["categorie_poste"],
                "competence_brute": comp,
                "famille": None,
                "competence_canonique": None,
                "source_extraction": "brut"
            })
        # Depuis l'extraction NLP sur description
        for comp_nlp in row.get("competences_nlp", []):
            lignes.append({
                "id_offre": row["id_offre"],
                "ville_clean": row["ville_clean"],
                "categorie_poste": row["categorie_poste"],
                "competence_brute": comp_nlp["competence"],
                "famille": comp_nlp["famille"],
                "competence_canonique": comp_nlp["competence"],
                "source_extraction": "nlp_description"
            })
            
    df_comp = pd.DataFrame(lignes)
    # Dedoublonner pour une meme offre
    return df_comp.drop_duplicates(subset=["id_offre", "competence_canonique", "source_extraction"])
