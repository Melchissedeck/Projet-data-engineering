import pandas as pd
from sqlalchemy import create_engine
from db_utils import connect_to_postgres
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
csv_file = os.path.join(base_dir, 'data', 'weatherHistory.csv')

table_name = 'weather_data'

try:
    df = pd.read_csv(csv_file)
    engine = connect_to_postgres()
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"✅ Données importées avec succès dans la table '{table_name}'.")

except Exception as e:
    print(f"❌ Une erreur s'est produite : {e}")
