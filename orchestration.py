import subprocess
import time

print("🚀 Démarrage de l’orchestration du pipeline météo")

try:
    # 1. Lancement du script d’import brut
    print("📥 Étape 1 : Import des données CSV dans PostgreSQL")
    subprocess.run(["python", "script-python/import_csv.py"], check=True)

    # 2. Pause brève si besoin
    time.sleep(2)

    # 3. Lancement de la transformation et monitoring
    print("🔄 Étape 2 : Transformation, enrichissement et historisation")
    subprocess.run(["python", "script-python/transform_monitor.py"], check=True)

    print("✅ Pipeline exécuté avec succès.")

except subprocess.CalledProcessError as e:
    print(f"❌ Échec lors de l'exécution d'un des scripts : {e}")
except Exception as e:
    print(f"❌ Erreur inattendue : {e}")
