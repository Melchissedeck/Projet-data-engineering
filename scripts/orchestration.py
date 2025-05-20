import subprocess
import time
import sys
import os

sql_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sql'))
sys.path.append(sql_dir)

print("🚀 Démarrage de l’orchestration du pipeline météo")

try:
    print("📥 Étape 1 : Import des données CSV dans PostgreSQL")
    subprocess.run(["python", os.path.join(sql_dir, "import_csv.py")], check=True)

    time.sleep(2)

    print("🔄 Étape 2 : Transformation, enrichissement et historisation")
    subprocess.run(["python", os.path.join(sql_dir, "transform_monitor.py")], check=True)

    print("✅ Pipeline exécuté avec succès.")

except subprocess.CalledProcessError as e:
    print(f"❌ Échec d'un script : {e}")
except Exception as e:
    print(f"❌ Erreur inattendue : {e}")
