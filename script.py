import pandas as pd
from sqlalchemy import create_engine
import getpass

username = 'postgres'
password = getpass.getpass(prompt='Entrez votre mot de passe PostgreSQL : ')
host = 'localhost'
port = '5432'
database = 'postgres'
table_name = 'weather_data'

csv_file = 'data/weatherHistory.csv'

try:
    df = pd.read_csv(csv_file)

    engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"✅ Données importées avec succès dans la table '{table_name}'.")

except Exception as e:
    print(f"❌ Une erreur s'est produite : {e}")
