\# BookWorld – Data Pipeline \& REST API - Projet pédagogique de Data Analyse 


\## 1. Présentation



BookWorld est une entreprise spécialisée dans la vente de livres en ligne.



L'objectif du projet est de construire un pipeline permettant de :



\- extraire des données provenant de plusieurs sources ;

\- nettoyer et enrichir les données ;

\- récupérer des informations complémentaires depuis un site web et une API ;

\- calculer des indicateurs de vente ;

\- stocker les résultats dans une base SQLite ;

\- exposer les données agrégées via une API REST.



Le projet applique également le principe de minimisation des données du RGPD.



\## 2. Sources de données



Le pipeline utilise plusieurs sources :



\- sales\_raw.csv : données brutes de ventes ;

\- bookworld\_reference.db : données de référence sur les pays, les canaux et les catégories ;

\- Books to Scrape (https://books.toscrape.com/) : informations sur les livres et leurs catégories ;

\- Frankfurter API : taux de change GBP → EUR.





\## 3. Structure du projet


bookworld\_project : pipeline.py, api.py, queries.sql, schema\_final.sql,  requirements.txt, README.md, .gitignore


data/ : sales_raw.csv, bookworld_reference

output_pipeline/ : bookworld_final.db




Principaux fichiers :



\- pipeline.py : Extraction, appel API, scraping, nettoyage, enrichissement, transformation, agrégation et chargement

\- api.py : API REST développée avec Flask

\- schema\_final.sql	Schéma de la base SQLite finale

\- queries.sql	Requêtes SQL d'extraction et de vérification

\- requirements.txt	Dépendances Python

\- .gitignore	Fichiers exclus du versionnement



\## 4. Installation



\### Prérequis

\- Python 3

\- Git



\### Installation des dépendances



Depuis le dossier du projet :



pip install -r requirements.txt



Les principales bibliothèques utilisées sont pandas, requests, beautifulsoup4 et flask.



\## 5. Exécution du pipeline



Lancer le pipeline avec :



python pipeline.py



Le pipeline réalise les principales étapes suivantes :



\- Extraction des ventes et des données de référence.

\- Scraping du catalogue de livres.

\- Récupération du taux de change GBP → EUR.

\- Nettoyage et conversion des données.

\- Enrichissement par jointures.

\- Calcul des revenus et des indicateurs.

\- Agrégation par pays, mois, canal, catégorie et groupe de canal.

\- Suppression des noms et prénoms des clients avant le stockage final.

\- Création de bookworld\_final.db et export des résultats au format CSV.



\## 6. Base de données finale



La base bookworld\_final.db contient notamment :



\- sales

\- countries

\- channels

\- category\_rules

\- sales\_by\_country

\- sales\_by\_country\_month

\- sales\_by\_country\_channel

\- sales\_by\_country\_category

\- sales\_by\_country\_channel\_group



\## 7. Lancement de l'API



Après l'exécution du pipeline, lancer :



python api.py



L'API est accessible à :



http://127.0.0.1:5000



\## 8. Authentification



L'accès aux endpoints est protégé par une clé API transmise dans le paramètre api-key de l'URL.



Exemple :



http://127.0.0.1:5000/health?api-key=bookworld0897



Une clé absente ou incorrecte entraîne une réponse HTTP 401.



La clé utilisée dans ce projet est une clé de démonstration et ne constitue pas un mécanisme de sécurité adapté à une application en production.



\## 9. Endpoints



Méthode : GET	

Endpoints :	

\- /health : Vérifie le fonctionnement de l'API et l'accès à la base

\- /sales-by-country : Ventes agrégées par pays

\- /sales-by-country-month : Ventes agrégées par pays et par mois

\- /sales-by-country-channel : Ventes agrégées par pays et par canal

\- /sales-by-country-category : Ventes agrégées par pays et par catégorie

\- /sales-by-country-channel-group : Ventes agrégées par pays et par groupe de canal



\## 10. RGPD



Le fichier sales\_raw.csv contient notamment les noms et prénoms des clients.



Ces données ne sont pas nécessaires aux analyses finales. Les colonnes `customer\_first\_name` et `customer\_last\_name` ne sont donc pas utilisées dans les analyses ni dans les agrégations, et ne sont pas exposées par les endpoints de l'API. Elles sont également supprimées avant le stockage dans la base finale.



Les fichiers locaux générés sont exclus du repository via .gitignore.



\## 11. Requêtes SQL et contrôles



Le fichier queries.sql contient :



\- les requêtes d'extraction des données de référence ;

\- une requête avec filtre sur les données actives ;

\- des vérifications de la présence des tables finales ;

\- des contrôles du nombre de lignes chargées.



Les endpoints de l'API ont également été testés localement avec la clé API.



\## 12. Versionnement



Le projet est versionné avec Git et publié sur GitHub.



Les fichiers nécessaires au fonctionnement et à la compréhension du projet sont versionnés dans le dépôt Git. Les fichiers générés par le pipeline restent exclus via .gitignore.


## Checklist d’exécution rapide

* [ ] **Installation**

  * Créer et activer un environnement virtuel
  * Installer les dépendances avec `requirements.txt`

* [ ] **Configuration**

  * Vérifier la présence des fichiers sources :

    * `sales_raw.csv`
    * `bookworld_reference.db`
  * Vérifier la configuration nécessaire au lancement de l’API

* [ ] **Pipeline**

  * Exécuter `pipeline.py`
  * Vérifier la création de `bookworld_final.db` et des fichiers générés

* [ ] **API**

  * Lancer `api.py`
  * Vérifier que l’API est accessible localement

* [ ] **Test des endpoints**

  * Tester `/health`
  * Tester les endpoints d’indicateurs avec la clé API

