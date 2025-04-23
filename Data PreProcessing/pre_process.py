import pandas as pd
import re

def preprocess_crash_data(csv_file):
    # Load the data
    df = pd.read_csv(csv_file)
    
    # Clean column names (remove spaces, standardize case)
    df.columns = [col.strip().lower().replace(' ', '_').replace('.', '_') for col in df.columns]
    
    # Extract key features
    features = {
        'accident_id': list(range(len(df))),  # Generate unique IDs
        'date': df['date_of_accident'].tolist(),
        'time': df['time_of_accident'].tolist(),
        'am_pm': df['time_of_accident'].apply(lambda x: 'AM' if pd.notna(x) and int(x.split(':')[0]) < 12 else 'PM' if pd.notna(x) else 'Unknown'),
        'location': df.apply(lambda row: f"{row.get('section_2__accident_information_1_0', '')}, {row.get('section_2__accident_information_1_1_0', '')}", axis=1).tolist(),
        'description': df.apply(lambda row: next((str(row[col]) for col in row.index if 'address_2' in col.lower() and pd.notna(row[col]) and len(str(row[col])) > 50), ""), axis=1).tolist(),
        'autonomous_mode': df.apply(lambda row: 'Yes' if row.get('autonomous_mode') == '/ ' else 'No', axis=1).tolist(),
        'vehicle_1_make': df['make'].tolist(),
        'vehicle_1_model': df['model'].tolist(),
        'vehicle_1_year': df['vehicle_year'].tolist(),
        'vehicle_1_moving': df.apply(lambda row: 'Yes' if row.get('moving') == '/ ' else 'No', axis=1).tolist(),
        'vehicle_2_make': df['make_2'].tolist() if 'make_2' in df.columns else [''] * len(df),
        'vehicle_2_model': df['model_2'].tolist(),
        'vehicle_2_year': df['vehicle_year_2'].tolist() if 'vehicle_year_2' in df.columns else [''] * len(df),
        'vehicle_2_moving': df.apply(lambda row: 'Yes' if row.get('moving_2') == '/ ' else 'No', axis=1).tolist(),
        'weather_conditions': df.apply(lambda row: extract_weather(row), axis=1).tolist(),
        'road_conditions': df.apply(lambda row: extract_road_conditions(row), axis=1).tolist(),
        'lighting_conditions': df.apply(lambda row: extract_lighting(row), axis=1).tolist(),
        'roadway_surface': df.apply(lambda row: extract_roadway_surface(row), axis=1).tolist(),
        'associated_factors': df.apply(lambda row: extract_associated_factors(row), axis=1).tolist(),
        'impact_points': df.apply(lambda row: extract_impact_points(row), axis=1).tolist(),
        'vehicle_damage': df.apply(lambda row: extract_vehicle_damage(row), axis=1).tolist(),
    }
    
    return pd.DataFrame(features)

# Extract weather conditions
def extract_weather(row):
    weather_cols = [col for col in row.index if 'weather' in col.lower() and pd.notna(row[col]) and row[col] == '/Yes']
    return ', '.join(weather_cols) if weather_cols else 'Not specified'

# Extract road conditions
def extract_road_conditions(row):
    road_cols = [col for col in row.index if 'road_conditions' in col.lower() and pd.notna(row[col]) and row[col] == '/Yes']
    return ', '.join(road_cols) if road_cols else 'Not specified'

# Extract lighting conditions
def extract_lighting(row):
    lighting_cols = [col for col in row.index if 'lighting' in col.lower() and pd.notna(row[col]) and row[col] == '/Yes']
    return ', '.join(lighting_cols) if lighting_cols else 'Not specified'

# Extract roadway surface conditions
def extract_roadway_surface(row):
    surface_cols = [col for col in row.index if col.startswith('roadway') and pd.notna(row[col]) and row[col] == '/Yes']
    return ', '.join(surface_cols) if surface_cols else 'Not specified'

# Extract associated factors
def extract_associated_factors(row):
    factor_cols = [col for col in row.index if col.startswith('other') and pd.notna(row[col]) and row[col] == '/Yes']
    return ', '.join(factor_cols) if factor_cols else 'Not specified'

# Extract impact points
def extract_impact_points(row):
    impact_cols = [col for col in row.index if any(x in col.lower() for x in ['rear', 'front', 'side']) and pd.notna(row[col]) and row[col] == '/Yes']
    return ', '.join(impact_cols) if impact_cols else 'Not specified'

# Extract vehicle damage based on column names
def extract_vehicle_damage(row):
    damage_levels = ["MINOR", "MAJOR", "MOD", "NONE", "UNK"]
    for level in damage_levels:
        damage_col = next((col for col in row.index if level.lower() in col.lower()), None)
        if damage_col and pd.notna(row[damage_col]) and row[damage_col] == '/Yes':
            return level
    return 'UNK'  # Default to 'UNKNOWN' if no damage level is found


# --- Execution ---
csv_file = ("C:\\Users\\ridah\\Desktop\\from desktop to new pc\\sENIOR rESEARCH pROJECT\\pdf Extraction\\pdf_extraction\\extracted_pdf_data_22024.csv")
processed_df = preprocess_crash_data(csv_file)

# Preview processed data
print(processed_df.head())

# Save the processed data
#processed_df.to_csv("C:\\Users\\ridah\\Desktop\\processed_crash_data.csv", index=False)
processed_df.to_csv("C:\\Users\\ridah\\Desktop\\from desktop to new pc\\sENIOR rESEARCH pROJECT\\pdf Extraction\\pdf_extraction\\processed_crash_data_22024.csv", index=False)
