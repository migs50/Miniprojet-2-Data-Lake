import json
import csv
import random
from datetime import datetime, timedelta
import os

# Liste de villes marocaines avec variantes (villes cibles et incoherences)
VILLES = ["Casablanca", "Rabat", "Tanger", "Marrakech", "Fs", "Agadir", "Oujda", "Knitra", "Ttouan", "Mekns", "Mohammedia", "El Jadida", "Settat", "Safi", "Beni Mellal"]

def generate_referentiel(filepath):
    ref = {
      "familles": {
        "langages": {
          "python": ["python", "python3", "py"],
          "javascript": ["javascript", "js", "node.js", "nodejs", "node"],
          "java": ["java", "java8", "java11", "java17"],
          "sql": ["sql", "mysql", "postgresql", "postgres", "oracle", "tsql"],
          "r": ["r", "rlang", "r-studio"],
          "php": ["php", "laravel", "symfony"]
        },
        "frameworks_web": {
          "react": ["react", "reactjs", "react.js"],
          "angular": ["angular", "angularjs"],
          "django": ["django", "django rest"],
          "spring": ["spring", "spring boot", "springboot"],
          "vuejs": ["vue", "vue.js", "vuejs"]
        },
        "data_engineering": {
          "spark": ["spark", "apache spark", "pyspark"],
          "kafka": ["kafka", "apache kafka"],
          "airflow": ["airflow", "apache airflow"],
          "dbt": ["dbt", "data build tool"],
          "hadoop": ["hadoop", "hdfs", "mapreduce"]
        },
        "cloud": {
          "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
          "gcp": ["gcp", "google cloud", "bigquery", "cloud storage"],
          "azure": ["azure", "microsoft azure", "synapse", "azure devops"]
        },
        "bi_analytics": {
          "power_bi": ["power bi", "powerbi", "pbi"],
          "tableau": ["tableau", "tableau desktop"],
          "metabase": ["metabase"],
          "looker": ["looker", "looker studio"],
          "excel": ["excel", "excel avance", "vba"]
        },
        "devops_infra": {
          "docker": ["docker", "docker compose"],
          "kubernetes": ["kubernetes", "k8s"],
          "jenkins": ["jenkins", "ci/cd"],
          "gitlab": ["gitlab", "gitlab ci"],
          "terraform": ["terraform"],
          "linux": ["linux", "bash", "shell"]
        },
        "methodologies": {
          "agile": ["agile", "scrum", "kanban", "sprint"],
          "git": ["git", "github", "bitbucket"]
        }
      }
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(ref, f, indent=2, ensure_ascii=False)
    print(f"[OK] Referentiel genere : {filepath}")

def generate_entreprises(filepath):
    entreprises = []
    types = ["SSII", "Produit", "Conseil", "Telecom", "Banque", "Autre"]
    tailles = ["Startup", "PME", "ETI", "Grande Entreprise"]
    secteurs = ["Informatique", "Finance", "Assurance", "E-commerce", "Sante", "Energie"]
    
    prefixes = ["Tech", "Data", "Cyber", "Cloud", "Net", "Web", "Synapse", "Nexus", "Pixel", "Code"]
    suffixes = ["Maroc", "Solutions", "Consulting", "Services", "Systems", "Labs", "Digital", "Innovations"]
    statuts = ["SARL", "SA", "SAS", "LLC"]
    
    for i in range(150):
        nom = f"{random.choice(prefixes)}{random.choice(suffixes)} {random.choice(statuts)}"
        ville = random.choices(VILLES, weights=[40, 20, 10, 5, 5, 5, 3, 3, 3, 2, 1, 1, 1, 0.5, 0.5])[0]
        entreprises.append({
            "nom_entreprise": nom,
            "secteur": random.choice(secteurs),
            "taille": random.choice(tailles),
            "ville_siege": ville,
            "site_web": f"www.{nom.lower().replace(' ', '').replace('.', '')}.ma",
            "type": random.choice(types)
        })
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=entreprises[0].keys())
        writer.writeheader()
        writer.writerows(entreprises)
    print(f"[OK] Entreprises generees : {filepath}")
    return entreprises

def generate_offres(filepath, entreprises):
    offres = []
    sources = ["rekrute", "marocannonce", "linkedin"]
    
    titres_base = [
        "Data Engineer", "Data Analyst", "Data Scientist", "Developpeur Full Stack",
        "Developpeur Backend", "Developpeur Frontend", "Ingenieur DevOps",
        "Chef de Projet IT", "Ingenieur Cybersecurite", "Developpeur React/Node.js"
    ]
    
    variants_titres = {
        "Data Engineer": ["Data Engineer", "Dev Data", "Ingenieur Big Data", "Data Eng.", "Ingenieur Data", "Data Engineer Junior"],
        "Developpeur Full Stack": ["Developpeur Full Stack", "Dev Full Stack", "Ingenieur Fullstack", "Developpeur React/Node.js"],
        "Data Analyst": ["Data Analyst", "Analyste Data", "Analyste BI", "Developpeur BI", "Analyste de donnees"],
    }
    
    contrats = ["CDI", "cdi", "Contrat a duree indeterminee", "Permanent", "CDD", "Freelance", "Stage"]
    experiences = ["0-1 an", "1-3 ans", "3-5 ans", "3 a 5 ans", "min 3 ans", "Debutant accepte", "5+ ans", "Senior"]
    teletravail = ["Presentiel", "Hybride", "Full Remote"]
    
    date_start = datetime(2023, 1, 1)
    
    comp_pool = ["React", "Node.js", "PostgreSQL", "Docker", "AWS", "Agile", "Git", "Python", "Spark", "SQL", "Java", "Kubernetes", "Linux", "Azure", "GCP", "Tableau", "Power BI", "Kafka", "Angular"]

    for i in range(5000):
        # 1. Source & IDs
        src = random.choice(sources)
        if src == "rekrute": idx = f"RK-{random.randint(2023, 2024)}-{random.randint(10000,99999)}"
        elif src == "linkedin": idx = f"LI-{random.randint(10000000,99999999)}"
        else: idx = f"MA-{random.randint(10000,99999)}"
        
        # 2. Titre de poste (Normal ou variante "sale")
        base = random.choice(titres_base)
        titre = random.choice(variants_titres.get(base, [base]))
        if random.random() < 0.2:
            titre = titre.lower()
            
        entreprise_obj = random.choice(entreprises)
        entreprise = entreprise_obj["nom_entreprise"]
        secteur = entreprise_obj["secteur"]
        
        # 3. Ville "sale"
        ville = entreprise_obj["ville_siege"]
        if random.random() < 0.3:
            ville = random.choice([ville.lower(), ville.upper(), ville + " ", "casa" if ville=="Casablanca" else ville])
            
        # 4. Salaire 
        rand_sal = random.random()
        if rand_sal < 0.25:
            salaire = random.choice(["Selon profil", "Confidentiel", "A negocier", None])
        elif rand_sal < 0.4:
            b = random.randint(10, 40)
            salaire = f"{b}K-{b+5}K"
        elif rand_sal < 0.5:
            salaire = f"{random.randint(2000, 4000)} EUR"
        else:
            b = random.randint(10000, 40000)
            salaire = f"{b}-{b+5000} MAD"
            
        # 5. Experience "sale"
        exp = random.choice(experiences) if random.random() < 0.9 else None
        
        # 6. Dates
        days_offset = random.randint(0, 690) # Entre Jan 2023 et Nov 2024
        pub_date = date_start + timedelta(days=days_offset)
        
        if random.random() < 0.05: # Probleme intentionnel: exp < pub
            exp_date = pub_date - timedelta(days=random.randint(1, 30))
        else:
            exp_date = pub_date + timedelta(days=random.randint(15, 60))
            
        pub_str = pub_date.strftime("%Y-%m-%d") if random.random() < 0.8 else pub_date.strftime("%d/%m/%Y")
        exp_str = exp_date.strftime("%Y-%m-%d") if random.random() < 0.8 else exp_date.strftime("%d/%m/%Y")

        # 7. Competences "sales" (separateurs)
        comps = random.sample(comp_pool, k=random.randint(3, 8))
        sep = random.choice([", ", "/", " - ", "  ", "\n", "|"])
        comp_brut = sep.join(comps)
        
        desc = f"Nous recherchons un profiltre {titre} pour rejoindre {entreprise}. Maitrise de {comp_brut}. Vous travaillerez sur des projets innovants."

        offres.append({
            "id_offre": idx,
            "source": src,
            "titre_poste": titre,
            "description": desc,
            "competences_brut": comp_brut,
            "entreprise": entreprise,
            "ville": ville,
            "type_contrat": random.choice(contrats),
            "experience_requise": exp,
            "salaire_brut": salaire,
            "niveau_etudes": random.choice(["Bac+3", "Bac+5", "Diplome d'Ingenieur", None]),
            "secteur": secteur,
            "date_publication": pub_str,
            "date_expiration": exp_str,
            "nb_postes": random.randint(1, 5),
            "teletravail": random.choice(teletravail),
            "langue_requise": random.sample(["Francais", "Anglais", "Arabe"], k=random.randint(1, 3))
        })
        
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(offres, f, indent=2, ensure_ascii=False)
    print(f"[OK] {len(offres)} offres generees : {filepath}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_referentiel("data/referentiel_competences_it.json")
    ent = generate_entreprises("data/entreprises_it_maroc.csv")
    generate_offres("data/offres_emploi_it_maroc.json", ent)
