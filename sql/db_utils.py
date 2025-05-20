from sqlalchemy import create_engine
import getpass

def connect_to_postgres():
    """
    Retourne une SQLAlchemy engine pour PostgreSQL (connexion sécurisée).
    """
    try:
        user = 'postgres'
        password = getpass.getpass(prompt='🔐 Entrez votre mot de passe PostgreSQL : ')
        host = 'localhost'
        port = '5432'
        dbname = 'postgres'

        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}')
        print("✅ Connexion réussie.")
        return engine
    except Exception as e:
        print(f"❌ Connexion échouée : {e}")
        return None
