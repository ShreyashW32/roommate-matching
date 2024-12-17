import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# Preprocess data function


def preprocess_data(data):
    # Fill missing values with 'No Preference' for categorical columns
    data = data.fillna('No Preference')
    names = data['Name']
    genders = data['Gender']  # Keep gender information separately
    # Keep roommate gender preference separately
    preferences = data['Preferred Gender of Roommate']
    # Remove non-numeric columns
    data = data.drop(
        columns=['Name', 'Index', 'Gender', 'Preferred Gender of Roommate'])

    # Ensure string columns like 'Hobbies' and 'Sports' are treated as strings
    for col in ['Hobbies', 'Sports']:
        if col in data.columns:
            data[col] = data[col].fillna("").astype(str)

    # Convert categorical columns to numeric using LabelEncoder
    le = LabelEncoder()
    for col in data.columns:
        if data[col].dtype == 'object' or data[col].dtype == 'string':
            data[col] = le.fit_transform(data[col].astype(str))

    # Normalize numerical columns
    scaler = MinMaxScaler()
    numeric_cols = data.select_dtypes(include=['int64', 'float64']).columns
    data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

    # Add back 'Name', 'Gender', and 'Preferred Gender of Roommate' columns
    data['Name'] = names
    data['Gender'] = genders
    data['Preferred Gender of Roommate'] = preferences
    return data

# Check gender compatibility


def is_gender_compatible(row1, row2):
    gender1 = row1['Gender']
    preference1 = row1['Preferred Gender of Roommate']
    gender2 = row2['Gender']
    preference2 = row2['Preferred Gender of Roommate']

    compatible1 = (preference1 == 'No Preference') or (preference1 == gender2)
    compatible2 = (preference2 == 'No Preference') or (preference2 == gender1)

    return compatible1 and compatible2

# Calculate match score using additional compatibility factors


def calculate_match(row1, row2):
    if not is_gender_compatible(row1, row2):
        return 0  # No compatibility due to gender preference

    # 1. Budget Compatibility
    budget1 = row1['Budget for Rent (Per Week AUD)']
    budget2 = row2['Budget for Rent (Per Week AUD)']
    budget_compatibility = 1 - abs(budget1 - budget2) / max(budget1, budget2)

    # 2. Age Compatibility
    age1 = row1['Age']
    age2 = row2['Age']
    age_compatibility = 1 - abs(age1 - age2) / max(age1, age2)

    # 3. Smoking Lifestyle Compatibility
    smoking1 = row1['Preferred Lifestyle (Smoking)']
    smoking2 = row2['Preferred Lifestyle (Smoking)']
    smoking_compatibility = 1 if smoking1 == smoking2 else 0

    # 4. Social Lifestyle Compatibility
    lifestyle1 = row1['Preferred Lifestyle']
    lifestyle2 = row2['Preferred Lifestyle']
    lifestyle_compatibility = 1 if lifestyle1 == lifestyle2 else 0

    # 5. Living Habits Compatibility
    living_habits1 = row1['Preferred Living Habits']
    living_habits2 = row2['Preferred Living Habits']
    living_habits_compatibility = 1 if living_habits1 == living_habits2 else 0

    # 6. Pets Compatibility
    pets1 = row1['Pets']
    pets2 = row2['Pets']
    pets_compatibility = 1 if pets1 == pets2 else 0

    # 7. Location Compatibility
    location1 = row1['Preferred Location/Neighborhood']
    location2 = row2['Preferred Location/Neighborhood']
    location_compatibility = 1 if location1 == location2 else 0

    # 8. Living Arrangement Compatibility
    living_arrangement1 = row1['Preferred Living Arrangement']
    living_arrangement2 = row2['Preferred Living Arrangement']
    living_arrangement_compatibility = 1 if living_arrangement1 == living_arrangement2 else 0

    # 9. Hobbies Compatibility
    hobbies1 = str(row1['Hobbies'])
    hobbies2 = str(row2['Hobbies'])
    hobbies_compatibility = len(set(hobbies1.split(",")).intersection(set(hobbies2.split(",")))) / \
        max(len(hobbies1.split(",")), len(hobbies2.split(",")), 1)

    # 10. Sports Compatibility
    sports1 = str(row1['Sports'])
    sports2 = str(row2['Sports'])
    sports_compatibility = len(set(sports1.split(",")).intersection(set(sports2.split(",")))) / \
        max(len(sports1.split(",")), len(sports2.split(",")), 1)

    # Combine all compatibility factors
    total_compatibility = (
        budget_compatibility +
        age_compatibility +
        smoking_compatibility +
        lifestyle_compatibility +
        living_habits_compatibility +
        pets_compatibility +
        location_compatibility +
        living_arrangement_compatibility +
        hobbies_compatibility +
        sports_compatibility
    ) / 10  # Averaging compatibility across all factors

    return total_compatibility

# Roommate matching function


def roommate_matching(file_path):
    data = pd.read_excel(file_path)  # Reading the uploaded file

    # Preprocess the data
    data = preprocess_data(data)

    match_scores = []

    # Iterate through all pairs to calculate match scores
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            score = calculate_match(data.iloc[i], data.iloc[j])
            match_scores.append(
                (data.iloc[i]['Name'], data.iloc[j]['Name'], score))

    matches = pd.DataFrame(match_scores, columns=[
                           'Person1', 'Person2', 'Match Score'])
    matches = matches.sort_values(by='Match Score', ascending=False)

    # Create individual tables for each person and keep only top 5 matches
    individual_tables = {}
    for name in data['Name']:
        person_matches = matches[(matches['Person1'] == name) | (
            matches['Person2'] == name)]
        person_matches = person_matches.reset_index(drop=True)

        # Get only the top 5 matches
        individual_tables[name] = person_matches.head(5)

    return matches, individual_tables
