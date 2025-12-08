import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from web.core.DataBase import exec_query

# --- 1. Récupération et préparation des données ---

# Les noms des mesures qui nous intéressent
mesure_names = ["colis 10kg GC", "colis 6100g GC"] #"colis 5kg GC"

all_data = []

for name in mesure_names:
    query = "SELECT time, T, mesure_name FROM Donnees WHERE mesure_name = ? ORDER BY time ASC"
    raw_data = exec_query(query=[query], parameter=[(name,)])
    all_data.extend(raw_data)

df = pd.DataFrame(all_data, columns=['time', 'temperature_c', 'mesure_name'])
df['time'] = pd.to_datetime(df['time'], unit='m')
df['time_elapsed_m'] = df.groupby('mesure_name')['time'].transform(lambda x: (x - x.min()).dt.total_seconds()//60)

print("Aperçu des données brutes:")
print(df.head())

# --- 2. Visualisation des courbes de température brutes ---
plt.figure(figsize=(12, 7))
# Créer un tracé pour chaque 'mesure_name'
for name in mesure_names:
    subset = df[df['mesure_name'] == name]
    plt.plot(subset['time_elapsed_m'], subset['temperature_c'], label=name)

plt.axhline(y=-77, color='r', linestyle='--', label='Température de sublimation de la GC (-77°C)')
plt.xlabel('Temps écoulé (minutes)')
plt.ylabel('Température (°C)')
plt.title('Courbes de Température pour différents poids de Glace Carbonique')
plt.legend()
plt.grid(True)
plt.savefig("1.png")

# --- 3. Extraction des métriques clés pour chaque mesure_name ---

results = []
temp_plateau_threshold = -77.0
tolerance = 2.0

for name in mesure_names:
    colis_df = df[df['mesure_name'] == name].sort_values(by='time_elapsed_m').copy()

    colis_df['temp_smooth'] = colis_df['temperature_c'].rolling(window=10, center=True, min_periods=1).mean()
    colis_df['temp_gradient'] = colis_df['temp_smooth'].diff() / colis_df['time_elapsed_m'].diff()
    
    plateau_start_idx = None
    for i in range(1, len(colis_df)):
        current_temp = colis_df.iloc[i]['temperature_c']
        prev_temp = colis_df.iloc[i-1]['temperature_c']
        current_gradient = colis_df.iloc[i]['temp_gradient']

        if (current_temp >= temp_plateau_threshold - tolerance and
            current_temp <= temp_plateau_threshold + tolerance):
            plateau_start_idx = i
            break

    plateau_end_idx = None
    if plateau_start_idx is not None:
        for i in range(plateau_start_idx + 1, len(colis_df)):
            current_temp = colis_df.iloc[i]['temperature_c']
            current_gradient = colis_df.iloc[i]['temp_gradient']
            if (current_temp > temp_plateau_threshold + tolerance):
                plateau_end_idx = i
                break
        if plateau_end_idx is None and colis_df.iloc[-1]['temperature_c'] <= temp_plateau_threshold + tolerance:
            plateau_end_idx = len(colis_df) - 1

    if plateau_start_idx is not None and plateau_end_idx is not None and plateau_end_idx > plateau_start_idx:
        time_start_plateau = colis_df.iloc[plateau_start_idx]['time_elapsed_m']
        time_end_plateau = colis_df.iloc[plateau_end_idx]['time_elapsed_m']
        duration_plateau = time_end_plateau - time_start_plateau
        
        remontee_start_time = time_end_plateau
        remontee_df = colis_df[colis_df['time_elapsed_m'] >= remontee_start_time].copy()

        speed_remontee_Cs = np.nan
        if len(remontee_df) > 1:
            fit_range_df = remontee_df[
                (remontee_df['temperature_c'] >= -60) & (remontee_df['temperature_c'] <= 0)
            ]
            
            if len(fit_range_df) > 5:
                x_fit = fit_range_df['time_elapsed_m'].values
                y_fit = fit_range_df['temperature_c'].values
                
                slope, intercept = np.polyfit(x_fit, y_fit, 1)
                speed_remontee_Cs = slope
    else:
        duration_plateau = np.nan
        speed_remontee_Cs = np.nan

    gc_weight_kg = np.nan
    if "10kg GC" in name:
        gc_weight_kg = 10.0
    elif "5kg GC" in name:
        gc_weight_kg = 5.0
    elif "1100g GC" in name:
        gc_weight_kg = 1.1

    results.append({
        'mesure_name': name,
        'gc_weight_kg': gc_weight_kg,
        'duration_plateau_m': duration_plateau,
        'speed_remontee_Cs': speed_remontee_Cs
    })

results_df = pd.DataFrame(results)
print("\nRésultats des métriques extraites:")
print(results_df)

# --- 4. Analyse des relations ---

# Relation Poids de GC -> Durée du plateau
plt.figure(figsize=(8, 6))
# Tracer les points
plt.scatter(results_df['gc_weight_kg'], results_df['duration_plateau_m'], s=100, label='Points de données')
# Ajouter les labels spécifiques pour chaque point
for i, row in results_df.iterrows():
    plt.annotate(row['mesure_name'], (row['gc_weight_kg'], row['duration_plateau_m']), textcoords="offset points", xytext=(5,5), ha='center')

plt.xlabel('Poids initial de Glace Carbonique (kg)')
plt.ylabel('Durée du Plateau (-77°C) (secondes)')
plt.title('Durée du Plateau en fonction du Poids de Glace Carbonique')
plt.grid(True)

clean_results_df = results_df.dropna(subset=['gc_weight_kg', 'duration_plateau_m'])
if len(clean_results_df) >= 2:
    slope, intercept = np.polyfit(clean_results_df['gc_weight_kg'], clean_results_df['duration_plateau_m'], 1)
    
    x_min_reg = clean_results_df['gc_weight_kg'].min()
    x_max_reg = clean_results_df['gc_weight_kg'].max()
    x_reg = np.array([x_min_reg, x_max_reg])
    y_reg = slope * x_reg + intercept
    
    plt.plot(x_reg, y_reg, color='red', linestyle='--', label=f'Régression linéaire: y = {slope:.2f}x + {intercept:.2f}')
    
    correlation = clean_results_df['gc_weight_kg'].corr(clean_results_df['duration_plateau_m'])
    plt.text(0.05, 0.95, f'Corrélation (Pearson): {correlation:.2f}', transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

plt.legend()
plt.savefig("2.png")

# Relation Poids de GC -> Vitesse de remontée
plt.figure(figsize=(8, 6))
plt.scatter(results_df['gc_weight_kg'], results_df['speed_remontee_Cs'], s=100, label='Points de données')
for i, row in results_df.iterrows():
    plt.annotate(row['mesure_name'], (row['gc_weight_kg'], row['speed_remontee_Cs']), textcoords="offset points", xytext=(5,5), ha='center')

plt.xlabel('Poids initial de Glace Carbonique (kg)')
plt.ylabel('Vitesse de Remontée (°C/seconde)')
plt.title('Vitesse de Remontée en fonction du Poids de Glace Carbonique')
plt.grid(True)

clean_results_df_speed = results_df.dropna(subset=['gc_weight_kg', 'speed_remontee_Cs'])
if len(clean_results_df_speed) >= 2:
    slope_s, intercept_s = np.polyfit(clean_results_df_speed['gc_weight_kg'], clean_results_df_speed['speed_remontee_Cs'], 1)
    
    x_min_reg_s = clean_results_df_speed['gc_weight_kg'].min()
    x_max_reg_s = clean_results_df_speed['gc_weight_kg'].max()
    x_reg_s = np.array([x_min_reg_s, x_max_reg_s])
    y_reg_s = slope_s * x_reg_s + intercept_s
    
    plt.plot(x_reg_s, y_reg_s, color='red', linestyle='--', label=f'Régression linéaire: y = {slope_s:.4f}x + {intercept_s:.4f}')

    correlation_s = clean_results_df_speed['gc_weight_kg'].corr(clean_results_df_speed['speed_remontee_Cs'])
    plt.text(0.05, 0.95, f'Corrélation (Pearson): {correlation_s:.2f}', transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

plt.legend()
plt.savefig("3.png")

# --- Interprétation et "loi" de relation ---
clean_results_df = results_df.dropna(subset=['gc_weight_kg', 'duration_plateau_m'])
if len(clean_results_df) >= 2:
    slope, intercept = np.polyfit(clean_results_df['gc_weight_kg'], clean_results_df['duration_plateau_m'], 1)
    print(f"\n--- Loi de relation Poids de GC -> Durée du Plateau ---")
    print(f"Durée_Plateau (secondes) = {slope:.2f} * Poids_GC_initial (kg) + {intercept:.2f}")
    print(f"Cela signifie qu'en moyenne, chaque kilogramme de glace carbonique supplémentaire prolonge le plateau de {slope/3600:.2f} heures.")
    
    clean_results_df_speed = results_df.dropna(subset=['gc_weight_kg', 'speed_remontee_Cs'])
    if len(clean_results_df_speed) >= 2:
        slope_s, intercept_s = np.polyfit(clean_results_df_speed['gc_weight_kg'], clean_results_df_speed['speed_remontee_Cs'], 1)
        print("\n--- Loi de relation Poids de GC -> Vitesse de Remontée ---")
        print(f"Vitesse_Remontée (°C/seconde) = {slope_s:.4f} * Poids_GC_initial (kg) + {intercept_s:.4f}")
        print("Comme mentionné, la vitesse de remontée est souvent plus liée à l'isolation du colis qu'à la quantité initiale de GC, une fois celle-ci sublimée. Le coefficient de corrélation peut aider à confirmer cela.")

results_json_path = 'analyse_resultats.json'
# Convertir le DataFrame en liste de dictionnaires pour l'exportation JSON
results_list = results_df.to_dict(orient='records')

# Écrire les données JSON dans un fichier
with open(results_json_path, 'w', encoding='utf-8') as f:
    json.dump(results_list, f, ensure_ascii=False, indent=4)

print(f"\nLes résultats ont été exportés dans '{results_json_path}'")