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
Lance simplement le script d’orchestration :
python orchestration.py
Le mot de passe PostgreSQL est demandé via le terminal.

# 📂 Structure du projet

.
├── data/
│   └── weatherHistory.csv
├── Scripts/
│   └── orchestration.py
├── SQL/
│   └── db_utils.py
│   └── import_csv.py
│   └── orchestration.py
└── README.md

# 🧩 SCHÉMA RELATIONNEL DE LA BASE DE DONNÉES

-- Table source
weather_data (
    "Formatted Date", "Summary", "Precip Type",
    "Temperature (C)", "Apparent Temperature (C)",
    "Humidity", "Wind Speed (km/h)", "Wind Bearing (degrees)",
    "Visibility (km)", "Loud Cover", "Pressure (millibars)",
    "Daily Summary"
)

-- Table transformée
weather_clean (
    id SERIAL PRIMARY KEY,
    formatted_date TIMESTAMP,
    summary TEXT,
    precip_type TEXT,
    temperature_c FLOAT,
    temperature_f FLOAT,
    apparent_temperature_c FLOAT,
    humidity FLOAT,
    humidity_level TEXT,
    wind_speed_kph FLOAT,
    wind_bearing_deg INTEGER,
    visibility_km FLOAT,
    is_foggy BOOLEAN,
    cloud_cover FLOAT,
    pressure_mb FLOAT,
    daily_summary TEXT,
    temperature_category TEXT,
    is_rainy BOOLEAN,
    is_snowy BOOLEAN
)

-- Table de log
weather_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    message TEXT,
    row_count INTEGER
)

-- Vue matérialisée (résumé quotidien)
weather_daily_summary (
    day DATE,
    avg_temp_c NUMERIC,
    avg_humidity NUMERIC,
    avg_wind_kph NUMERIC,
    observations INTEGER
)
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
                | - Clean & enrich    |
                | - Historise         |
                | - Vue matérialisée |
                +----------+----------+
                           |
                           v
                +----------------------+
                | Base PostgreSQL      |
                | Tables :             |
                | - weather_clean      |
                | - weather_log        |
                | - weather_daily_summary (VIEW)
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
