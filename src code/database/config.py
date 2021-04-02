""" script for loading configuration data - db name and paths to csv files locations.
"""

with open("database/config.txt", 'r') as f:
    db_name = f.readline().strip()
    # dataset_path = f.readline().strip()
    # country_codes_path = f.readline().strip()
    # feature_classes_path = f.readline().strip()
    # feature_codes_path = f.readline().strip()
    # trip_types_path = f.readline().strip()
    # trip_seasons_path = f.readline().strip()
    # reviews_path = f.readline().strip()