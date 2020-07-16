from tyrapp import app
from tyrapp import munge as Munge
import zipfile
import os
app_root = app.config['APP_ROOT']
get_served = os.path.join(app_root, 'get_served')
if(not os.path.exists(get_served)):
    os.mkdir(get_served)

# Function to write a single string to a TXT
def write_to_TXT(input_str, filename = "data", destination_path = get_served):
    with open(f"{destination_path}/{filename}.txt", "w") as f:
        f.write(input_str)

# Function to write a list of dictionaries to TXTs
def write_list_to_TXTs(input_list, destination_path = get_served):
    for d in input_list:
        filename = Munge.scrubPunct(d["name"])[:30]
        write_to_TXT(d["text"], filename, destination_path)

# Function to zip a list of files.
def zip_list_of_files(filename_list, destination_path, filename):
    filepath_list = [os.path.join(get_served, filename) for filename in filename_list]
    with zipfile.ZipFile(f"{destination_path}/{filename}", 'w') as zipMe:        
        for i, filename in enumerate(filename_list):
            zipMe.write(filepath_list[i], filename, compress_type=zipfile.ZIP_DEFLATED)

# Function to empty get_served directory
def cleanup():
    for file_name in os.listdir(get_served):
        file_path = os.path.join(get_served, file_name)
        os.remove(file_path)
