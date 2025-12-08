import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

# --- 1. Chargement des Résultats depuis le fichier JSON ---
results_json_path = 'analyse_resultats.json'

try:
    with open(results_json_path, 'r', encoding='utf-8') as f:
        results_data = json.load(f)
    model_df = pd.DataFrame(results_data)
    print("Données chargées depuis JSON:")
    print(model_df)
except FileNotFoundError:
    print(f"Erreur: Le fichier '{results_json_path}' n'a pas été trouvé. Exécutez d'abord le script d'analyse.")
    exit()

# S'assurer que les colonnes numériques sont bien des nombres
model_df['gc_weight_kg'] = pd.to_numeric(model_df['gc_weight_kg'], errors='coerce')
model_df['duration_plateau_m'] = pd.to_numeric(model_df['duration_plateau_m'], errors='coerce')
model_df['speed_remontee_Cs'] = pd.to_numeric(model_df['speed_remontee_Cs'], errors='coerce')
model_df['temp_at_end_plateau_c'] = pd.to_numeric(model_df['duration_plateau_m'], errors='coerce')

# Supprimer les lignes avec des valeurs NaN pour les colonnes d'intérêt
model_df_cleaned_duration = model_df.dropna(subset=['gc_weight_kg', 'duration_plateau_m'])
model_df_cleaned_speed = model_df.dropna(subset=['gc_weight_kg', 'speed_remontee_Cs'])

# --- 2. Modélisation de la Loi "Poids -> Durée du Plateau" (avec test polynomial) ---
print("\n--- Modélisation : Poids de Glace Carbonique vs. Durée du Plateau (Test de fonctions) ---")

if len(model_df_cleaned_duration) >= 2:
    X_duration = model_df_cleaned_duration['gc_weight_kg'].values
    y_duration = model_df_cleaned_duration['duration_plateau_m'].values

    # Créer un ensemble de points pour tracer les courbes lissées
    # Cela couvre la plage de vos poids de GC observés
    x_plot = np.linspace(X_duration.min() - 0.5, X_duration.max() + 0.5, 100)

    plt.figure(figsize=(10, 7))
    plt.scatter(X_duration, y_duration, s=150, zorder=5, label='Données réelles', edgecolors='black') # zorder pour mettre les points au-dessus

    # --- Modèle Linéaire (Degré 1) ---
    if len(X_duration) >= 2:
        coeffs_linear = np.polyfit(X_duration, y_duration, 1)
        poly_linear = np.poly1d(coeffs_linear)
        y_pred_linear = poly_linear(X_duration)
        r2_linear = 1 - (np.sum((y_duration - y_pred_linear) ** 2) / np.sum((y_duration - np.mean(y_duration)) ** 2))
        
        plt.plot(x_plot, poly_linear(x_plot), color='blue', linestyle='-', label=f'Linéaire (y={coeffs_linear[0]:.2f}x+{coeffs_linear[1]:.2f}, R²={r2_linear:.2f})')
        print(f"\nModèle Linéaire (Degré 1):")
        print(f"  Durée_Plateau (min) = {coeffs_linear[0]:.2f} * Poids_GC_initial (kg) + {coeffs_linear[1]:.2f}")
        print(f"  R²: {r2_linear:.2f}")
    else:
        print("Pas assez de points pour un modèle linéaire.")

    # --- Modèle Quadratique (Degré 2) ---
    if len(X_duration) >= 3: # Nécessite au moins 3 points pour un polynôme de degré 2
        coeffs_quadratic = np.polyfit(X_duration, y_duration, 2)
        poly_quadratic = np.poly1d(coeffs_quadratic)
        y_pred_quadratic = poly_quadratic(X_duration)
        r2_quadratic = 1 - (np.sum((y_duration - y_pred_quadratic) ** 2) / np.sum((y_duration - np.mean(y_duration)) ** 2))
        
        plt.plot(x_plot, poly_quadratic(x_plot), color='green', linestyle='--', label=f'Quadratique (R²={r2_quadratic:.2f})')
        print(f"\nModèle Quadratique (Degré 2):")
        print(f"  Durée_Plateau (min) = {coeffs_quadratic[0]:.2f}x² + {coeffs_quadratic[1]:.2f}x + {coeffs_quadratic[2]:.2f}")
        print(f"  R²: {r2_quadratic:.2f}")
    else:
        print("Pas assez de points pour un modèle quadratique (nécessite au moins 3 points).")

    # --- Modèle Cubique (Degré 3) ---
    if len(X_duration) >= 4: # Nécessite au moins 4 points pour un polynôme de degré 3
        coeffs_cubic = np.polyfit(X_duration, y_duration, 3)
        poly_cubic = np.poly1d(coeffs_cubic)
        y_pred_cubic = poly_cubic(X_duration)
        r2_cubic = 1 - (np.sum((y_duration - y_pred_cubic) ** 2) / np.sum((y_duration - np.mean(y_duration)) ** 2))
        
        plt.plot(x_plot, poly_cubic(x_plot), color='purple', linestyle=':', label=f'Cubique (R²={r2_cubic:.2f})')
        print(f"\nModèle Cubique (Degré 3):")
        print(f"  Durée_Plateau (min) = {coeffs_cubic[0]:.2f}x³ + {coeffs_cubic[1]:.2f}x² + {coeffs_cubic[2]:.2f}x + {coeffs_cubic[3]:.2f}")
        print(f"  R²: {r2_cubic:.2f}")
    else:
        print("Pas assez de points pour un modèle cubique (nécessite au moins 4 points).")
        print("Avec 3 points, un modèle quadratique passera toujours parfaitement par les points (R²=1), mais il est crucial d'avoir plus de données pour généraliser.")


    plt.xlabel('Poids initial de Glace Carbonique (kg)')
    plt.ylabel('Durée du Plateau (-77°C) (minutes)')
    plt.title('Comparaison des Modèles: Durée du Plateau vs. Poids de Glace Carbonique')
    plt.legend()
    plt.grid(True)
    plt.savefig("model_duration_comparison.png")
    plt.show()
    plt.close()

else:
    print("Pas assez de points de données valides pour modéliser la durée du plateau (nécessite au moins 2 points).")


# --- 3. Modélisation de la Loi "Poids -> Vitesse de Remontée" (reste linéaire pour l'instant) ---
# Généralement, la vitesse de remontée dépend plus de l'isolation une fois la GC sublimée.
# Nous conservons la régression linéaire ici, mais vous pouvez appliquer les mêmes tests polynomiaux
# si vous suspectez une non-linéarité pour cette relation aussi.
print("\n--- Modélisation : Poids de Glace Carbonique vs. Vitesse de Remontée ---")

if len(model_df_cleaned_speed) >= 2:
    X_speed = model_df_cleaned_speed['gc_weight_kg'].values
    y_speed = model_df_cleaned_speed['speed_remontee_Cs'].values

    slope_speed, intercept_speed = np.polyfit(X_speed, y_speed, 1)

    print(f"Loi: Vitesse_Remontée (°C/seconde) = {slope_speed:.4f} * Poids_GC_initial (kg) + {intercept_speed:.4f}")

    y_pred_speed = slope_speed * X_speed + intercept_speed

    ss_total_s = np.sum((y_speed - np.mean(y_speed)) ** 2)
    ss_residual_s = np.sum((y_speed - y_pred_speed) ** 2)
    r2_speed = 1 - (ss_residual_s / ss_total_s) if ss_total_s > 0 else np.nan
    mse_speed = np.mean((y_speed - y_pred_speed) ** 2)

    print(f"Coefficient de détermination (R²): {r2_speed:.2f}")
    print(f"Erreur Quadratique Moyenne (MSE): {mse_speed:.2f}")

    plt.figure(figsize=(8, 6))
    plt.scatter(X_speed, y_speed, s=100, label='Données réelles')
    plt.plot(X_speed, y_pred_speed, color='red', linestyle='--', label=f'Modèle linéaire (R²={r2_speed:.2f})')
    plt.xlabel('Poids initial de Glace Carbonique (kg)')
    plt.ylabel('Vitesse de Remontée (°C/seconde)')
    plt.title('Modèle: Vitesse de Remontée vs. Poids de Glace Carbonique')
    plt.legend()
    plt.grid(True)
    plt.savefig("model_speed.png")
    plt.show()
    plt.close()

else:
    print("Pas assez de points de données valides pour modéliser la vitesse de remontée (nécessite au moins 2 points).")

# --- Note sur la modélisation avancée et le nombre de points ---
print("\n--- Important : Nombre de Points de Données ---")
print("Avec seulement 3 points de données (1.1kg, 5kg, 10kg), un modèle quadratique passera *parfaitement* par les trois points, résultant en un R² de 1.0. ")
print("Cependant, cela ne signifie pas que le modèle est bon pour *prédire* des valeurs intermédiaires ou extérieures à cette plage.")
print("Pour une modélisation robuste et pour valider si une non-linéarité est réelle, il est fortement recommandé d'avoir plus de points de données (par exemple, 2kg, 7kg, etc.).")