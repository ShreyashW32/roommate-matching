import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

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
    # Gender of person 1 and their preference
    gender1 = row1['Gender']
    preference1 = row1['Preferred Gender of Roommate']
    # Gender of person 2 and their preference
    gender2 = row2['Gender']
    preference2 = row2['Preferred Gender of Roommate']

    # Check if preferences are compatible
    compatible1 = (preference1 == 'No Preference') or (preference1 == gender2)
    compatible2 = (preference2 == 'No Preference') or (preference2 == gender1)

    return compatible1 and compatible2

# Calculate match score using additional compatibility factors


def calculate_match(row1, row2):
    # Check gender compatibility first
    if not is_gender_compatible(row1, row2):
        return 0  # No compatibility due to gender preference

    # Calculate compatibility for various factors
    budget1 = row1['Budget for Rent (Per Week AUD)']
    budget2 = row2['Budget for Rent (Per Week AUD)']
    budget_compatibility = 1 - abs(budget1 - budget2) / max(budget1, budget2)

    age1 = row1['Age']
    age2 = row2['Age']
    age_compatibility = 1 - abs(age1 - age2) / max(age1, age2)

    smoking1 = row1['Preferred Lifestyle (Smoking)']
    smoking2 = row2['Preferred Lifestyle (Smoking)']
    smoking_compatibility = 1 if smoking1 == smoking2 else 0

    lifestyle1 = row1['Preferred Lifestyle']
    lifestyle2 = row2['Preferred Lifestyle']
    lifestyle_compatibility = 1 if lifestyle1 == lifestyle2 else 0

    living_habits1 = row1['Preferred Living Habits']
    living_habits2 = row2['Preferred Living Habits']
    living_habits_compatibility = 1 if living_habits1 == living_habits2 else 0

    pets1 = row1['Pets']
    pets2 = row2['Pets']
    pets_compatibility = 1 if pets1 == pets2 else 0

    location1 = row1['Preferred Location/Neighborhood']
    location2 = row2['Preferred Location/Neighborhood']
    location_compatibility = 1 if location1 == location2 else 0

    living_arrangement1 = row1['Preferred Living Arrangement']
    living_arrangement2 = row2['Preferred Living Arrangement']
    living_arrangement_compatibility = 1 if living_arrangement1 == living_arrangement2 else 0

    hobbies1 = str(row1['Hobbies'])
    hobbies2 = str(row2['Hobbies'])
    hobbies_compatibility = len(set(hobbies1.split(",")).intersection(set(hobbies2.split(",")))) / \
        max(len(hobbies1.split(",")), len(hobbies2.split(",")), 1)

    sports1 = str(row1['Sports'])
    sports2 = str(row2['Sports'])
    sports_compatibility = len(set(sports1.split(",")).intersection(set(sports2.split(",")))) / \
        max(len(sports1.split(",")), len(sports2.split(",")), 1)

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


def roommate_matching(data):
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


# Example usage (replace 'roommate_data.xlsx' with your file)
# Set the file path
file_path = r"C:\Users\shrey\Downloads\TRAVEL DOCS FINAL\roomate_data4.xlsx"
data = pd.read_excel(file_path)  # Reading the file from the specified path
matches, individual_tables = roommate_matching(data)

# Display overall top matches
print("Top Matches:")
print(matches.head())

# Display individual tables with only the top 5 matches for each person
for person, table in individual_tables.items():
    print(f"\nTop Matches for {person}:")
    print(table)
