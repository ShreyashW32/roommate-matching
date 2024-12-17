import pandas as pd
import pickle  # For saving preprocessed data and results
# Import the roommate matching function
from roommate_algorithm import roommate_matching

# File path for the dataset
file_path = r"C:\Users\shrey\Downloads\TRAVEL DOCS FINAL\roomate_data4.xlsx"

try:
    # Load the dataset
    print("Loading dataset...")
    data = pd.read_excel(file_path)

    # Process the data and generate matches
    print("Processing data and generating matches...")
    matches, individual_tables = roommate_matching(data)

    # Save results to a pickle file for later use
    pickle_file_path = 'roommate_results.pkl'
    with open(pickle_file_path, 'wb') as f:
        pickle.dump((matches, individual_tables), f)

    print(f"Results successfully saved to {pickle_file_path}")

except FileNotFoundError:
    print(
        f"Error: File not found at {file_path}. Please check the path and try again.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
