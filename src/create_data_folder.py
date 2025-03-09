import os

def create_data_folder():
    """
    Creates a 'data' directory if it does not exist.
    """
    folder_path = "data/raw"
    
    try:
        os.makedirs(folder_path, exist_ok=True)  # Creates folder if it doesn't exist
        print(f"📂 Folder '{folder_path}' is ready for storing CSV files.")
    except Exception as e:
        print(f"❌ Error creating folder '{folder_path}': {e}")

# Example usage
if __name__ == "__main__":
    create_data_folder()
