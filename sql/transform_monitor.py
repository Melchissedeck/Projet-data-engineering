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

        # === 8. Création des tables du modèle en étoile ===
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_date (
                date_id SERIAL PRIMARY KEY,
                full_date DATE UNIQUE,
                year INT,
                month INT,
                day INT,
                weekday TEXT
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_weather_type (
                weather_type_id SERIAL PRIMARY KEY,
                summary TEXT,
                precip_type TEXT,
                is_rainy BOOLEAN,
                is_snowy BOOLEAN,
                daily_summary TEXT,
                UNIQUE(summary, precip_type, is_rainy, is_snowy, daily_summary)
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_conditions (
                condition_id SERIAL PRIMARY KEY,
                humidity_level TEXT,
                temperature_category TEXT,
                is_foggy BOOLEAN,
                UNIQUE(humidity_level, temperature_category, is_foggy)
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_weather (
                fact_id SERIAL PRIMARY KEY,
                formatted_date TIMESTAMP,
                date_id INT REFERENCES dim_date(date_id),
                weather_type_id INT REFERENCES dim_weather_type(weather_type_id),
                condition_id INT REFERENCES dim_conditions(condition_id),
                temperature_c FLOAT,
                temperature_f FLOAT,
                apparent_temperature_c FLOAT,
                humidity FLOAT,
                wind_speed_kph FLOAT,
                wind_bearing_deg INT,
                visibility_km FLOAT,
                cloud_cover FLOAT,
                pressure_mb FLOAT
            );
        """))

        # === 9. Peuplement des dimensions ===
        connection.execute(text("""
            INSERT INTO dim_date (full_date, year, month, day, weekday)
            SELECT DISTINCT 
                DATE(formatted_date),
                EXTRACT(YEAR FROM formatted_date)::INT,
                EXTRACT(MONTH FROM formatted_date)::INT,
                EXTRACT(DAY FROM formatted_date)::INT,
                TO_CHAR(formatted_date, 'Day')
            FROM weather_clean
            ON CONFLICT (full_date) DO NOTHING;
        """))

        connection.execute(text("""
            INSERT INTO dim_weather_type (summary, precip_type, is_rainy, is_snowy, daily_summary)
            SELECT DISTINCT summary, precip_type, is_rainy, is_snowy, daily_summary
            FROM weather_clean
            ON CONFLICT DO NOTHING;
        """))

        connection.execute(text("""
            INSERT INTO dim_conditions (humidity_level, temperature_category, is_foggy)
            SELECT DISTINCT humidity_level, temperature_category, is_foggy
            FROM weather_clean
            ON CONFLICT DO NOTHING;
        """))

        # === 10. Peuplement de la table de faits ===
        connection.execute(text("""
            INSERT INTO fact_weather (
                formatted_date, date_id, weather_type_id, condition_id,
                temperature_c, temperature_f, apparent_temperature_c,
                humidity, wind_speed_kph, wind_bearing_deg,
                visibility_km, cloud_cover, pressure_mb
            )
            SELECT 
                wc.formatted_date,
                dd.date_id,
                wt.weather_type_id,
                cond.condition_id,
                wc.temperature_c,
                wc.temperature_f,
                wc.apparent_temperature_c,
                wc.humidity,
                wc.wind_speed_kph,
                wc.wind_bearing_deg,
                wc.visibility_km,
                wc.cloud_cover,
                wc.pressure_mb
            FROM weather_clean wc
            JOIN dim_date dd ON DATE(wc.formatted_date) = dd.full_date
            JOIN dim_weather_type wt ON
                wc.summary = wt.summary AND
                wc.precip_type IS NOT DISTINCT FROM wt.precip_type AND
                wc.is_rainy = wt.is_rainy AND
                wc.is_snowy = wt.is_snowy AND
                wc.daily_summary = wt.daily_summary
            JOIN dim_conditions cond ON
                wc.humidity_level = cond.humidity_level AND
                wc.temperature_category = cond.temperature_category AND
                wc.is_foggy = cond.is_foggy;
        """))

        print("🌟 Modèle en étoile mis à jour avec succès.")

except Exception as e:
    print(f"❌ Une erreur s’est produite : {e}")