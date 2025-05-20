from db_utils import connect_to_postgres
from sqlalchemy import text
from datetime import datetime

# Connexion avec SQLAlchemy engine
engine = connect_to_postgres()
if engine is None:
    exit()

try:
    print("🚀 Début du processus de transformation et monitoring...")

    with engine.connect() as connection:

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_clean (
                id SERIAL PRIMARY KEY,
                observation_time TIMESTAMP,
                temperature_c FLOAT,
                humidity FLOAT,
                wind_kph FLOAT,
                weather_summary TEXT
            );
        """))

        connection.execute(text("""
            INSERT INTO weather_clean (observation_time, temperature_c, humidity, wind_kph, weather_summary)
            SELECT 
                "Formatted Date"::timestamp,
                "Temperature (C)",
                "Humidity",
                "Wind Speed (km/h)",
                "Summary"
            FROM weather_data wd
            WHERE "Temperature (C)" IS NOT NULL
              AND "Humidity" IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM weather_clean wc
                  WHERE wc.observation_time = "Formatted Date"::timestamp
              );
        """))

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
            "msg": f'Transformation exécutée le {datetime.now()}',
            "count": row_count
        })

        result = connection.execute(text("SELECT MAX(observation_time) FROM weather_clean;"))
        latest_time = result.scalar()

        print("✅ Données transformées et historisées avec succès.")
        print(f"📊 Dernière donnée insérée : {latest_time}")
        print(f"📈 Total de lignes dans `weather_clean` : {row_count}")

except Exception as e:
    print(f"❌ Une erreur s’est produite : {e}")
