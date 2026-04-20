import pandas as pd
import re
from datetime import datetime

# Dictionnaires de normalisation
VILLES_MAP = {
    "casa": "Casablanca", "casablanca": "Casablanca", "casablanca ": "Casablanca", "casablance": "Casablanca",
    "rabat": "Rabat", "rabat ": "Rabat",
    "tanger": "Tanger", "tanger ": "Tanger", "tangier": "Tanger",
    "marrakech": "Marrakech", "marrakesh": "Marrakech",
    "fes": "Fs", "fez": "Fs", "fès": "Fs", "fès ": "Fs",
    "agadir": "Agadir", "oujda": "Oujda", "kénitra": "Knitra", "kenitra": "Knitra",
    "tétouan": "Ttouan", "tetouan": "Ttouan", "meknès": "Mekns", "meknes": "Mekns",
}

TITRES_MAP = {
    "Data Engineer": ["data engineer", "data eng", "ingenieur data", "ingénieur data", "dev data", "ingenieur big data"],
    "Data Analyst": ["data analyst", "analyste data", "analyste de donnees", "analyste bi", "bi analyst"],
    "Data Scientist": ["data scientist", "machine learning engineer", "ml engineer", "ingenieur ia"],
    "Developpeur Full Stack": ["developpeur full stack", "full stack", "full-stack", "fullstack", "react/node"],
    "Developpeur Backend": ["developpeur backend", "backend developer", "developpeur java", "developpeur python"],
    "Developpeur Frontend": ["developpeur frontend", "frontend developer", "developpeur react", "developpeur angular"],
    "Ingenieur DevOps": ["devops", "sre", "cloud engineer", "ingenieur infrastructure"],
    "Chef de Projet IT": ["chef de projet", "project manager", "scrum master", "product owner"],
    "Ingenieur Cybersecurite": ["cybersecurite", "cybersecurity", "analyste soc", "pentester", "securite"]
}

def normaliser_ville(ville_brute):
    if not ville_brute or pd.isna(ville_brute): return "Inconnue"
    cle = str(ville_brute).strip().lower()
    return VILLES_MAP.get(cle, str(ville_brute).strip().title())

def normaliser_titre(titre_brut):
    if not titre_brut or pd.isna(titre_brut): return "Autre"
    cle = str(titre_brut).strip().lower()
    for cat, vars in TITRES_MAP.items():
        if any(v in cle for v in vars): return cat
    return "Autre"

def parser_salaire(salaire_brut):
    """Extrait [min_mad, max_mad] depuis le texte brut."""
    if not salaire_brut or pd.isna(salaire_brut): return None, None
    s = str(salaire_brut).strip().lower()
    if s in ["selon profil", "confidentiel", "a negocier"]: return None, None
    
    taux = 11 if "eur" in s else 1
    
    # Range en K (ex: 15K-20K)
    m = re.search(r'(\d+)\s*k\s*-\s*(\d+)\s*k', s)
    if m: return int(m.group(1)) * 1000 * taux, int(m.group(2)) * 1000 * taux
    
    # Range standard (ex: 15000-20000)
    m = re.search(r'(\d{4,6})\s*-\s*(\d{4,6})', s)
    if m: return int(m.group(1)) * taux, int(m.group(2)) * taux
    
    # Valeur fixe en EUR
    m = re.search(r'(\d{4,6})\s*eur', s)
    if m: return int(m.group(1)) * taux, int(m.group(1)) * taux
    
    return None, None

def parser_experience(exp_brut):
    if not exp_brut or pd.isna(exp_brut): return None, None
    s = str(exp_brut).strip().lower()
    if any(kw in s for kw in ["debutant", "0-1", "0 a"]): return 0, 1
    m = re.search(r'(\d+)\s*[-a]\s*(\d+)', s)
    if m: return int(m.group(1)), int(m.group(2))
    m = re.search(r'(?:min.*?|plus de\s*|\+)?(\d+)\s*(?:\+|ans?)', s)
    if m: return int(m.group(1)), int(m.group(1)) + 3
    return None, None

def parser_date(date_str):
    if not date_str or pd.isna(date_str): return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try: return datetime.strptime(str(date_str).strip(), fmt)
        except ValueError: continue
    return None

def valider_dates(pub, exp):
    if pub is None or exp is None: return True
    return pub <= exp
