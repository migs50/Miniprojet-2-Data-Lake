
# réalisé par:  khadija dridri et Khouala Bouchame

# Rapport de Traitement du Pipeline Data

Ce document trace les opérations de nettoyage et d'enrichissement NLP effectuées lors de la phase **Silver** du Data Lake `mexora_rh_lake`. L'objectif est d'assurer la transparence sur l'altération et la qualité des données selon les directives de Data Gouvernance.

---

## 1. Normalisation des Titres de Postes (`titre_poste`)

**Règle appliquée :**
Application de patterns d'expressions régulières (Regex) pour re-catégoriser le texte libre en grandes familles standard (ex: "Data Engineer", "Cloud Engineer"). Les alias, les abréviations et le pluriel sont gérés. 

**Volumétrie :**
- **Avant :** ~2 000 titres uniques non standardisés.
- **Après :** 9 grandes familles de profils de référence IT homogènes.

**Cas limites et traitement :**
- *Cas limite :* Les offres avec des noms internes cryptiques (ex: "Développeur N3") ou hors charte.
- *Traitement :* Les expressions ne correspondent pas, le poste prend la valeur de replis `Autre IT`. Au lieu d'être rejetée et de corrompre le comptage volumétrique total, la ligne est conservée et classifiée comme résiduelle.

---

## 2. Normalisation des Salaires (`salaire_brut`)

**Règle appliquée :**
Extraction des montants numériques via Regex. Conversion d'une fourchette (min/max) et imputation d'un `salaire_median_mad` mathématique. 
Si le montant contient `"K"`, il est multiplié par 1 000. S'il contient `"EUR"` ou `"€"`, on applique le taux de conversion fixe `1 EUR = 10,8 MAD`.

**Volumétrie :**
- **Avant :** 5 000 lignes avec chaînes de caractères brutes (mélange K, EUR, MAD).
- **Après :** 5 000 lignes conservées, création des champs numériques propres (`salaire_min_mad`, `salaire_max_mad`, `salaire_median_mad`) et de l'indicateur d'exploitabilité `salaire_connu` (Booléen).
- *Taux de complétion moyen observé* : ~75% de salaires exploitables.

**Cas limites et traitement :**
- *Cas limite 1 (Mentions obfusquées) :* Valeurs type "Selon profil", "Confidentiel" ou valeur vide `null`.
- *Traitement :* Positionné sur `salaire_connu = False`. Les valeurs numériques sont `None`.
- *Cas limite 2 (Aberrations) :* Un recruteur saisit un salaire mensuel de "200 MAD" par accident.
- *Traitement :* Un filtre d'intégrité borne la plage acceptable entre `3 000` et `100 000` MAD. Les valeurs en-dehors sont ignorées (`salaire_connu = False`).

---

## 3. Extraction de l'Expérience (`experience_requise`)

**Règle appliquée :**
Conversion des descriptions RH d'expérience en deux limites numériques strictes (`experience_min_ans` et `experience_max_ans`). Les fourchettes (3-5 ans), les minimas (min 3 ans) et les sémantiques (Junior, Senior) sont converties séparément.

**Volumétrie :**
- **Avant :** 5 000 lignes avec des descriptions textuelles libres d'expérience.
- **Après :** 5 000 lignes conservées (enrichies avec les colonnes `experience_min_ans` et `experience_max_ans`).

**Cas limites et traitement :**
- *Débutant implicite :* "Débutant", "Junior", "Stage" $\Rightarrow$ Plage codée artificiellement à `(0, 2)`.
- *Senior implicite :* "Expert", "Lead", "Confirmé" $\Rightarrow$ Seuil min codé à `5`, seuil max reste ouvert (`None`).
- *Cas indécodable :* Si aucune règle ne matche, la règle ne force rien et renvoie `(None, None)`.

---

## 4. Enrichissement NLP des Compétences IT

**Règle appliquée :**
Le script `silver_nlp.py` récupère les champs `competences_brut` et le corpus total `description`. Il utilise les limites de mots (`\b`) pour confronter l'intégralité du texte à un référentiel normatif de 300+ compétences via un balayage Regex.
La donnée plate d'une offre est éclatée (unnest) pour créer un fichier relationnel de liaison *Offre $\leftrightarrow$ Compétence*.

**Volumétrie :**
- **Avant :** 5 000 lignes d'offres contenant de la donnée textuelle agglomérée.
- **Après :** Plus de ~32 000 lignes générées dans la table des dimensions `competences.parquet`. Une offre peut donc représenter de 1 à N lignes dans cette nouvelle table. 

**Cas limites et traitement :**
- *Cas limite 1 (Chevauchement phonétique) :* Repérer "React" mais éviter "ReactJS". Repérer "Node" mais privilégier "Node.js".
- *Traitement :* Le dictionnaire d'alias est **trié par longueur décroissante** avant le balayage. L'algorithme valide la compétence composite la plus longue et évite les sous-matchs (le mot long intercepte le texte de gauche en premier).
- *Cas limite 2 (Aucune compétence) :* L'offre RH est vide de sens ou ne mentionne aucun mot-clef du référentiel.
- *Traitement :* L'offre crée artificiellement une ligne unique avec la compétence positionnée à `non_détecté` et famille `inconnu`. Celà permet de toujours tracer la présence de l'offre et d'éviter les orphelins (perte de ligne) lors des jointures SQL.
