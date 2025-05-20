from db_utils import connect_to_postgres
from sqlalchemy import text
from datetime import datetime

# Connexion via SQLAlchemy engine
engine = connect_to_postgres()
if engine is None:
    exit()

try:
    print("🚀 Début du processus de transformation, enrichissement et monitoring...")

    with engine.begin() as connection:

        # === 1. Supprimer et recréer la table weather_clean avec toutes les colonnes ===
        connection.execute(text("DROP TABLE IF EXISTS weather_clean;"))

        connection.execute(text("""
            CREATE TABLE weather_clean (
                id SERIAL PRIMARY KEY,
                formatted_date TIMESTAMP,
                summary TEXT,
                precip_type TEXT,
                temperature_c FLOAT,
                apparent_temperature_c FLOAT,
                humidity FLOAT,
                wind_speed_kph FLOAT,
                wind_bearing_deg INTEGER,
                visibility_km FLOAT,
                cloud_cover FLOAT,
                pressure_mb FLOAT,
                daily_summary TEXT
            );
        """))

        # === 2. Insérer les données depuis weather_data ===
        connection.execute(text("""
            INSERT INTO weather_clean (
                formatted_date, summary, precip_type, temperature_c,
                apparent_temperature_c, humidity, wind_speed_kph,
                wind_bearing_deg, visibility_km, cloud_cover,
                pressure_mb, daily_summary
            )
            SELECT 
                "Formatted Date"::timestamp,
                "Summary",
                "Precip Type",
                "Temperature (C)",
                "Apparent Temperature (C)",
                "Humidity",
                "Wind Speed (km/h)",
                "Wind Bearing (degrees)",
                "Visibility (km)",
                "Loud Cover",
                "Pressure (millibars)",
                "Daily Summary"
            FROM weather_data
            WHERE "Temperature (C)" IS NOT NULL
              AND "Humidity" IS NOT NULL;
        """))

        # === 3. Créer (si nécessaire) la table de log ===
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                row_count INTEGER
            );
        """))

        # === 4. Ajouter une entrée dans le log ===
        result = connection.execute(text("SELECT COUNT(*) FROM weather_clean;"))
        row_count = result.scalar()

        connection.execute(text("""
            INSERT INTO weather_log (message, row_count)
            VALUES (:msg, :count);
        """), {
            "msg": f'Transformation exécutée le {datetime.now()}',
            "count": row_count
        })

        # === 5. Créer la vue matérialisée pour résumé journalier ===
        connection.execute(text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS weather_daily_summary AS
            SELECT 
                DATE(formatted_date) AS day,
                ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp_c,
                ROUND(AVG(humidity)::numeric, 2) AS avg_humidity,
                ROUND(AVG(wind_speed_kph)::numeric, 2) AS avg_wind_kph,
                COUNT(*) AS observations
            FROM weather_clean
            GROUP BY day
            ORDER BY day;
        """))

        # === 6. Rafraîchir la vue à chaque exécution ===
        connection.execute(text("REFRESH MATERIALIZED VIEW weather_daily_summary;"))

        # === 7. Monitoring console ===
        result = connection.execute(text("SELECT MAX(formatted_date) FROM weather_clean;"))
        latest_time = result.scalar()

        print("✅ Données transformées, enrichies et historisées avec succès.")
        print(f"📊 Dernière donnée insérée : {latest_time}")
        print(f"📈 Total de lignes dans `weather_clean` : {row_count}")

except Exception as e:
    print(f"❌ Une erreur s’est produite : {e}")
