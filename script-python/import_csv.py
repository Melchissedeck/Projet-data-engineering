import pandas as pd
from db_utils import connect_to_postgres

csv_file = './data/weatherHistory.csv'
table_name = 'weather_data'

try:
    df = pd.read_csv(csv_file)

    engine = connect_to_postgres()
    if engine is None:
        raise Exception("Échec de la connexion à PostgreSQL.")

    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"✅ Données importées avec succès dans la table '{table_name}'.")

except Exception as e:
    print(f"❌ Une erreur s'est produite : {e}")
