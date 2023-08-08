import snowflake.connector
import pandas as pd
import datetime
import json
import os

# Load configurations from JSON files
current_directory = os.getcwd()
config_folder_path = os.path.join(current_directory, "config")
config_path = os.path.join(config_folder_path, "audt_config.json")
config = json.load(open(config_path, "r"))
options_path = os.path.join(config_folder_path, "Audt_options_selected.json")
options = json.load(open(options_path, "r"))
creds = config["Credentials"]

# Create the Snowflake connection using snowflake.connector
conn = snowflake.connector.connect(
    user=creds["user"],
    password=creds["password"],
    account=creds["account"],
    warehouse=creds["warehouse"],
    database=creds["database"],
    schema=creds["schema"],
    role=creds["role"],
)

# Print connection status
print('connected successfully with snowflake')

# Get today's date and create a folder to store audit outputs
today = datetime.date.today()
today_str = today.strftime('%Y %m %d')
cs = conn.cursor()

current_directory = os.getcwd()
directory_path = os.path.join(current_directory, "Audit Outputs", today_str)

if not os.path.exists(directory_path):
    os.makedirs(directory_path)

# Iterate through each audit option
for i, audit in enumerate(options["Audits"]):
    print(f"Performing {audit['Audit Name']}")

    table_dfs = []
    
    # Create the DataFrame for each table in the audit
    for table, sheet_name_without_ext in audit["Table Sheet Name Mapping"].items():
        try:
            # Execute the SQL query using the cursor
            cs.execute(f'SELECT * FROM LOGICBI_PRD.{table}')
            # Fetch all the data and column names
            df = pd.DataFrame(cs.fetchall(), columns=[col[0] for col in cs.description])
        except Exception as e:
            # Catch any exception and handle it as needed
            print(f"An error occurred while querying table {table}: {e}")
            continue  # Continue to the next table in case of an error
        
        # Apply style to highlight mismatched keywords
        df_highlighted = df.style.applymap(
            lambda x: f'background-color: {config["Background Color"]}' if isinstance(x, str) and x in config["Mismatch Keywords"] else ''
        )
        table_dfs.append({
            "df": df_highlighted,
            "sheet_name_without_ext": sheet_name_without_ext
        })

    # Write the audit tables to separate sheets in an Excel file
    with pd.ExcelWriter(os.path.join(directory_path, f"{audit['Audit Name']}.xlsx")) as writer:
        for table in table_dfs:
            table["df"].to_excel(
                writer,
                table["sheet_name_without_ext"] if table["sheet_name_without_ext"] else "Sheet 1",
                index=False
            )    
    
    print(f"{i+1} {audit['Audit Name']} completed.")
    
print('All audits are completed.')
