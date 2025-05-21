# 🌦️ PIPELINE MÉTÉO – PostgreSQL & Python
# 📌 PRÉSENTATION DU PROJET
Ce projet met en place un pipeline de traitement de données météo depuis un fichier CSV brut vers une base de données PostgreSQL, avec enrichissement, historisation et monitoring. Il est conçu pour démontrer un workflow de type ETL (Extract, Transform, Load) automatisé via Python.

Étapes principales :

Importation des données CSV dans PostgreSQL

Transformation & enrichissement des données (unités, catégories, indicateurs)

Historisation et log d’exécution

Création d’une vue matérialisée pour résumer les données météo par jour

Orchestration automatique de toutes les étapes

# ▶️ INSTRUCTIONS D’EXÉCUTION
🔧 Prérequis
Python 3.8+

PostgreSQL installé localement (par défaut : user postgres, base postgres)

Fichier CSV weatherHistory.csv dans le dossier ./data/

📦 Installation des dépendances

pip install pandas sqlalchemy psycopg2

🚀 Exécution du pipeline

python orchestration.py

Le mot de passe PostgreSQL est demandé via le terminal.

# 📂 Structure du projet


├── data/

│   └── weatherHistory.csv

├── docs/

│   └── Projet-Data-Engineering-Pipeline-ELT.pdf

├── Scripts/

│   └── orchestration.py

├── SQL/

│   └── db_utils.py

│   └── import_csv.py

│   └── transform_monitor.py

└── README.md

# 🧩 SCHÉMA RELATIONNEL DE LA BASE DE DONNÉES

![image](https://github.com/user-attachments/assets/47df5e05-d38a-468a-bbe8-c36d5d15e21c)


# 🔄 SCHÉMA DU PIPELINE

                +---------------------+
                | weatherHistory.csv  |
                +----------+----------+
                           |
                           v
                +----------+----------+
                |  import_csv.py      |
                |  (import brut)      |
                +----------+----------+
                           |
                           v
                +----------+----------+
                | transform_monitor.py|
                | - Nettoyer, enrichir|
                | - Transformer       |
                +----------+----------+
                           |
                           v
                +----------------------+
                | Base PostgreSQL      |
                | Tables :             |
                | - weather_data       |
                | - weather_clean      | 
                | - fact_weather       | 
                | - dim_conditions     | 
                | - dim_date           | 
                | - dim_weather_type   | 
                | - weather_log        |
                +----------------------+

                          ▲
                          |
         +----------------+----------------+
         |  orchestration.py (pipeline)    |
         +---------------------------------+
# 📈 Enrichissements ajoutés
Conversion Température °F

Catégorisation température : Froid, Doux, Chaud

Catégorisation humidité : Sec, Confortable, Humide

Drapeaux météo : is_rainy, is_snowy, is_foggy

👤 Auteur
Projet réalisé par : 
- Mehdi BENCHEIKH
- Théo CHANNAROND
- Ashwin DEVADEVAN
- Melchissedeck AFOUDAH
