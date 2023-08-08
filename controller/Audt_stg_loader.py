# Import required modules
import snowflake.connector
import pandas as pd
import datetime
import json
import os
import subprocess
import threading
import datetime

#Locating the root directory
current_directory = os.getcwd()

# Create a thread lock to ensure only one subprocess runs at a time
lock = threading.Lock()
lock.acquire()
try:
    # Execute the subprocess to run 'Audt_file_namer.py'
    controller_path=os.path.join(current_directory,"controller")
    file_namer_path=os.path.join(controller_path,"Audt_file_namer.py")
    subprocess.run(['python', file_namer_path])
finally:
    # Release the lock after the subprocess has finished
    lock.release()

# Load configuration from 'Audt_config.json' file
config_folder_path=os.path.join(current_directory,"config")
config_path = os.path.join(config_folder_path, "audt_config.json")
config = json.load(open(config_path, "r"))

# Extract credentials from the configuration
creds = config["Credentials"]

# Connect to Snowflake using the extracted credentials
conn = snowflake.connector.connect(
    user=creds["user"],
    password=creds["password"],
    account=creds["account"],
    warehouse=creds["warehouse"],
    database=creds["database"],
    schema=creds["schema"],
    role=creds["role"],
)

# Get the current date and format it to string in 'YYYY-MM-DD' format
today = datetime.date.today()
today_str = today.strftime('%Y-%m-%d')

# Create a cursor to execute SQL queries on the Snowflake connection
cs = conn.cursor()

# Print successful connection message to Snowflake
print('Connected successfully with Snowflake')

# Get the current directory and set a subdirectory 'Source'
source_directory = os.path.join(current_directory, "Source")

# Iterate through the files in the 'Source' directory
for filename in os.scandir(source_directory):
    if filename.is_file():
        # Replace backslashes with forward slashes to get the stage path for Snowflake
        stage_path = filename.path.replace("\\", "/")
        try:
            # Use the Snowflake PUT command to load the file into the 'GBS_AUDT_INTERNAL' stage
            cs.execute(f"PUT 'file://{stage_path}' @GBS_AUDT_INTERNAL OVERWRITE=TRUE;")
            print(f"{filename.path} has been loaded")
        except Exception as e:
            # Print any exception that occurs during the loading process
            print(e)

# Print a message indicating that files have been successfully loaded into 'GBS_AUDT_INTERNAL'
print("Files successfully loaded into GBS_AUDT_INTERNAL")
print()
print()

# Get the current weekday (0 = Monday, 6 = Sunday)
current_weekday = datetime.datetime.now().weekday()

# Perform actions based on the weekday
if current_weekday == 0:  # Monday
    print("Monday! Time to start the week.")
    cs.execute("CALL REGULAR_AUDITS();")
elif current_weekday == 1:  # Tuesday
    print("Happy Tuesday!")
    cs.execute("CALL TUESDAY_AUDITS();")
    print("This requires extra time.")
elif current_weekday == 2:  # Wednesday
    print("It's Wednesday, almost there now.")
    cs.execute("CALL REGULAR_AUDITS();")
elif current_weekday == 3:  # Thursday
    print("Thursday is almost the end of the week!")
    cs.execute("CALL THURSDAY_AUDITS();")
elif current_weekday == 4:  # Friday
    print("TGIF! Time to relax -> soon.")
    cs.execute("CALL FRIDAY_AUDITS();")
elif current_weekday == 5:  # Saturday
    print("Enjoy your Saturday, the procedure can't be called today.")
else:  # Sunday
    print("Sunday is supposed to be a day of rest :'[ ")
    cs.execute("CALL REGULAR_AUDITS();")

print("The procedures are being called, TAKE 2 SIPS OF YOUR COFFEE BEFORE DOWNLOADING OUTPUT.")