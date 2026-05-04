# Projet Data Lake — Mexora RH Intelligence
# réalisé par: khadija dridri et Khouala Bouchame
Ce projet implémente une architecture Data Lake complète pour ingérer, transformer et analyser les offres d'emploi IT au Maroc (scrappées depuis Rekrute, LinkedIn et MarocAnnonce).

## 🗂 Structure du Projet

L'architecture suit un découpage en zones logiques traditionnelles (Bronze, Silver, Gold).

```text
.
├── mexora_rh_lake/
│   ├── data/
│   │   ├── offres_emploi_it_maroc.json        # Dataset brut
│   │   └── referentiel_competences_it.json    # Référentiel des compétences
│   ├── pipeline/
│   │   ├── bronze_ingestion.py      # Chargement brut et partitionnement
│   │   ├── silver_transform.py      # Nettoyage des salaires, règles métiers
│   │   ├── silver_nlp.py            # Extraction NLP des compétences
│   │   └── gold_aggregation.py      # Calcul des tables analytiques DuckDB
│   ├── analysis/
│   │   └── analyse_marche.py        # Requêtes métier sur la table Gold
│   ├── data_lake/                   # Stockage physique des fichiers (Bronze/Silver/Gold)
│   ├── main.py                      # Orchestrateur
│   └── requirements.txt             # Dépendances Python
└── analyse_marche_it_maroc.ipynb    # Notebook d'analyse métier (DuckDB)
```

## ⚙️ Instructions d'Installation et d'Exécution

### 1. Prérequis
Assurez-vous d'avoir Python 3.9+ installé.

Installez les dépendances nécessaires :
```bash
pip install -r requirements.txt
```
*(Dépendances majeures : `pandas`, `pyarrow`, `duckdb`)*

### 2. Lancer le pipeline complet
Le script d'orchestration global s'occupe de lancer toutes les étapes séquentiellement (Génération des données factices si absentes -> Ingestion Bronze -> Transformation Silver -> Traitement Gold -> Analyse DRH Terminal).

Exécutez depuis la racine (`mexora_rh_lake/`) :
```bash
python main.py
```

### 3. Exécuter unitairement les scripts
Si vous souhaitez développer ou tester une zone spécifique, vous pouvez charger les modules manuellement. L'architecture est totalement découplée.

*Exemple pour re-générer uniquement la zone Silver :*
```python
from pipeline.silver_transform import charger_depuis_bronze, nettoyer_titres_postes, normaliser_salaires
from pipeline.silver_nlp import extraire_competences, sauvegarder_silver

# ... appliquer les fonctions ...
```

## 📊 Explorer les résultats
Toutes les tables finales générées se trouvent dans : `data_lake/gold/` (ou `data_lake_mexora_rh/gold/`).
Étant au format `Parquet`, elles sont hautement compressées et optimisées pour la lecture. Vous pouvez les ouvrir avec DuckDB, Pandas, Excel (avec le module PowerQuery) ou directement dans un outil BI comme Tableau ou PowerBI.

## 📈 Analyse du Marché (Nouveautés)

Suite à la mise en place du Data Lake, un outil d'analyse basé sur **DuckDB** et **Jupyter Notebook** a été ajouté à la racine du projet :

- **`analyse_marche_it_maroc.ipynb`** : Analyse métier complète avec requêtes DuckDB sur la couche Gold (compétences demandées, salaires médians, corrélation expérience-salaire, etc.).

Pour exécuter ces notebooks, assurez-vous d'avoir installé les dépendances (dont `jupyter`, `duckdb`, `matplotlib`, `seaborn`) et lancez :
```bash
jupyter notebook
```
