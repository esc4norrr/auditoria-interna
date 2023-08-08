import pandas as pd
import datetime
import json
import os
import re

today = datetime.date.today()
today_str = today.strftime('%Y-%m-%d')
current_directory = os.getcwd()
source_directory = os.path.join(current_directory, "source")
for entry in os.scandir(source_directory):
    if entry.is_file() and entry.name.endswith('.csv'):
        old_file_path = os.path.join(source_directory, entry.name)

        new_filename = re.sub(r'\d+(?=\.[^.]+$)', '', entry.name)
        new_file_path = os.path.join(source_directory, new_filename)

        try:
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {entry.name} -> {new_filename}")
        except Exception as e:
            print(f"Failed to rename {entry.name}: {e}")
