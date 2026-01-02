"""
Résumé de l'exécution des tests
Génère un rapport simple des tests
"""
import subprocess
import sys
import json
from datetime import datetime


def run_tests():
    """Execute tous les tests et génère un rapport"""
    print("="*70)
    print("🧪 Exécution de la suite de tests ProjetELK")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Tests unitaires
    print("📦 Tests unitaires...")
    result_unit = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/', '-m', 'unit', '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    # Tests d'intégration
    print("🔗 Tests d'intégration...")
    result_integration = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/', '-m', 'integration', '-v', '--tb=short'],
        capture_output=True,
        text=True
    )
    
    # Tous les tests avec coverage
    print("📊 Tests complets avec coverage...")
    result_all = subprocess.run(
        ['python3', '-m', 'pytest', 'tests/', '-v', '--cov=webapp', '--cov-report=term', '--cov-report=html'],
        capture_output=True,
        text=True
    )
    
    print("\n" + "="*70)
    print("✅ Tests terminés")
    print("="*70)
    
    # Afficher les résultats
    print(result_all.stdout)
    if result_all.returncode != 0:
        print(result_all.stderr)
        sys.exit(1)
    
    return result_all.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
