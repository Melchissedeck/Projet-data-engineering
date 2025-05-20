from db_utils import connect_to_postgres
from sqlalchemy import text
from datetime import datetime

engine = connect_to_postgres()
if engine is None:
    exit()

try:
    print("🚀 Début du processus de transformation, enrichissement et monitoring...")

    with engine.begin() as connection:

        # 1. Supprimer la vue matérialisée puis la table pour éviter les dépendances
        connection.execute(text("DROP MATERIALIZED VIEW IF EXISTS weather_daily_summary;"))
        connection.execute(text("DROP TABLE IF EXISTS weather_clean;"))

        # 2. Recréer la table enrichie
        connection.execute(text("""
            CREATE TABLE weather_clean (
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
            );
        """))

        # 3. Insertion enrichie depuis weather_data
        connection.execute(text("""
            INSERT INTO weather_clean (
                formatted_date, summary, precip_type, temperature_c, temperature_f,
                apparent_temperature_c, humidity, humidity_level, wind_speed_kph,
                wind_bearing_deg, visibility_km, is_foggy, cloud_cover, pressure_mb,
                daily_summary, temperature_category, is_rainy, is_snowy
            )
            SELECT 
                "Formatted Date"::timestamp,
                "Summary",
                "Precip Type",
                "Temperature (C)",
                ("Temperature (C)" * 9/5 + 32),
                "Apparent Temperature (C)",
                "Humidity",
                CASE
                    WHEN "Humidity" < 0.3 THEN 'Sec'
                    WHEN "Humidity" < 0.7 THEN 'Confortable'
                    ELSE 'Humide'
                END,
                "Wind Speed (km/h)",
                "Wind Bearing (degrees)",
                "Visibility (km)",
                "Visibility (km)" < 1.0,
                "Loud Cover",
                "Pressure (millibars)",
                "Daily Summary",
                CASE
                    WHEN "Temperature (C)" < 5 THEN 'Froid'
                    WHEN "Temperature (C)" < 20 THEN 'Doux'
                    ELSE 'Chaud'
                END,
                "Precip Type" = 'rain',
                "Precip Type" = 'snow'
            FROM weather_data
            WHERE "Temperature (C)" IS NOT NULL
              AND "Humidity" IS NOT NULL;
        """))

        # 4. Historisation
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                row_count INTEGER
            );
        """))

        result = connection.execute(text("SELECT COUNT(*) FROM weather_clean;"))
        row_count = result.scalar()

        connection.execute(text("""
            INSERT INTO weather_log (message, row_count)
            VALUES (:msg, :count);
        """), {
            "msg": f'Transformation enrichie exécutée le {datetime.now()}',
            "count": row_count
        })

        # 5. Vue matérialisée recréée
        connection.execute(text("""
            CREATE MATERIALIZED VIEW weather_daily_summary AS
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

        # 6. Refresh de la vue
        connection.execute(text("REFRESH MATERIALIZED VIEW weather_daily_summary;"))

        # 7. Monitoring
        result = connection.execute(text("SELECT MAX(formatted_date) FROM weather_clean;"))
        latest_time = result.scalar()

        print("✅ Données transformées et enrichies avec succès.")
        print(f"📊 Dernière donnée insérée : {latest_time}")
        print(f"📈 Total de lignes dans `weather_clean` : {row_count}")

except Exception as e:
    print(f"❌ Une erreur s’est produite : {e}")
