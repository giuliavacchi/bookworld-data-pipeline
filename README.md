# BookWorld – Data Pipeline & REST API

Projet pédagogique de Data Analyse

## 1. Présentation

BookWorld est une entreprise spécialisée dans la vente de livres en ligne.

L'objectif du projet est de construire un pipeline permettant de :

* Extraire des données provenant de plusieurs sources
* Nettoyer et enrichir les données
* Récupérer des informations complémentaires depuis un site web et une API
* Calculer des indicateurs de vente
* Stocker les résultats dans une base SQLite
* Exposer les données agrégées via une API REST

Le projet applique également le principe de minimisation des données du RGPD.

## 2. Sources de données

Le pipeline utilise plusieurs sources :

* sales_raw.csv : données brutes de ventes
* bookworld_reference.db : données de référence sur les pays, les canaux et les catégories
* Books to Scrape : informations sur les livres et leurs catégories
* Frankfurter API : taux de change GBP → EUR

## 3. Structure du projet

```text
bookworld_project/
├── bookworld_reference.db
├── sales_raw.csv
├── pipeline.py
├── api.py
├── queries.sql
├── schema_final.sql
├── README.md
├── requirements.txt
├── .gitignore
└── bookworld_final.db
```
* data/ : sales_raw.csv, bookworld_reference
* output_pipeline/ : bookworld_final.db, fichiers CSV

### Principaux fichiers

* `pipeline.py` : extraction, appel API, scraping, nettoyage, enrichissement, transformation, agrégation et chargement
* `api.py` : API REST développée avec Flask
* `schema_final.sql` : schéma de la base SQLite finale
* `queries.sql` : requêtes SQL d'extraction et de vérification
* `requirements.txt` : dépendances Python
* `.gitignore` : fichiers exclus du versionnement

## 4. Installation

### Prérequis

* Python 3
* Git

### Installation des dépendances

Depuis le dossier du projet :

```bash
pip install -r requirements.txt
```

Les principales bibliothèques utilisées sont `pandas`, `requests`, `beautifulsoup4` et `flask`.

## 5. Exécution du pipeline

Lancer le pipeline avec :

```bash
python pipeline.py
```

Le pipeline réalise les principales étapes suivantes :

* Extraction des ventes et des données de référence
* Scraping du catalogue de livres
* Récupération du taux de change GBP → EUR
* Nettoyage et conversion des données
* Enrichissement par jointures
* Calcul des revenus et des indicateurs
* Agrégation par pays, mois, canal, catégorie et groupe de canal
* Suppression des noms et prénoms des clients avant le stockage final
* Création de bookworld_final.db et export des résultats au format CSV

## 6. Base de données finale

La base bookworld_final.db contient notamment :

* sales
* countries
* channels
* category_rules
* sales_by_country
* sales_by_country_month
* sales_by_country_channel
* sales_by_country_category
* sales_by_country_channel_group

## 7. Lancement de l'API

Après l'exécution du pipeline, lancer :

```bash
python api.py
```

L'API est accessible à :

```text
http://127.0.0.1:5000
```

## 8. Authentification

Les endpoints d'indicateurs sont protégés par une clé API transmise dans le paramètre api-key de l'URL.

Exemple :

```text
http://127.0.0.1:5000/sales-by-country?api-key=bookworld0897
```

Une clé absente ou incorrecte entraîne une réponse HTTP `401`.

L'endpoint /health est accessible sans clé API afin de permettre de vérifier la disponibilité de l'API et de la base de données.

La clé utilisée dans ce projet est une clé de démonstration et ne constitue pas un mécanisme de sécurité adapté à une application en production.

## 9. Endpoints

Méthode : GET

* /health : vérifie le fonctionnement de l'API et l'accès à la base
* /sales-by-country : ventes agrégées par pays
* /sales-by-country-month : ventes agrégées par pays et par mois
* /sales-by-country-channel : ventes agrégées par pays et par canal
* /sales-by-country-category : ventes agrégées par pays et par catégorie
* /sales-by-country-channel-group : ventes agrégées par pays et par groupe de canal

## 10. RGPD

Le fichier sales_raw.csv contient notamment les noms et prénoms des clients.

Ces données ne sont pas nécessaires aux analyses finales. Les colonnes customer_first_name et customer_last_name ne sont donc pas utilisées dans les analyses ni dans les agrégations. Elles ne sont pas exposées par les endpoints de l'API et sont supprimées avant le stockage dans la base finale.


## 11. Requêtes SQL et contrôles

Le fichier queries.sql contient :

* les requêtes d'extraction des données de référence
* une requête avec filtre sur les données actives
* des vérifications de la présence des tables finales
* des contrôles du nombre de lignes chargées

Les endpoints de l'API ont également été testés localement avec la clé API.

## 12. Versionnement

Le projet est versionné avec Git et publié sur GitHub.

Les fichiers nécessaires au fonctionnement et à la compréhension du projet sont versionnés dans le dépôt Git. Les fichiers générés par le pipeline restent exclus via .gitignore.

## 13. Checklist d'exécution rapide

* [ ] **Installation**

  * Créer et activer un environnement virtuel
  * Installer les dépendances avec requirements.txt

* [ ] **Configuration**

  * Vérifier la présence des fichiers sources :

    * sales_raw.csv
    * bookworld_reference.db
    * schema_final.sql

* [ ] **Pipeline**

  * Exécuter pipeline.py
  * Vérifier la création de bookworld_final.db et des fichiers générés

* [ ] **API**

  * Lancer api.py
  * Vérifier que l'API est accessible localement

* [ ] **Test des endpoints**

  * Tester /health sans clé API
  * Tester les endpoints d'indicateurs avec la clé API
