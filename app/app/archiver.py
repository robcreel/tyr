import zipfile
import os

# Function to get first n items in a list, if there are that many.
def get_top_n(input_list, n):
    n = min(n, len(input_list))
    return(input_list[:n])

# Function to write a single string to a TXT
def write_to_TXT(input_str, filename = "data", destination_path = "./get_served"):
    with open(f"{destination_path}/file_{filename}.txt", "w") as f:
        f.write(input_str)

# Function to write a list of dictionaries to TXTs
def write_list_to_TXTs(input_list, destination_path = "./get_served"):
    for d in input_list:
        write_to_TXT(d["text"], d["name"] , destination_path)

# Function to zip a list of files.
def zip_list_of_files(input_list, destination_path, filename):
    with zipfile.ZipFile(f"{destination_path}/{filename}", 'w') as zipMe:        
        for file in input_list:
            zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)

# Function to empty get_served directory
def cleanup():
    for path in os.listdir("./get_served"):
        os.remove(path)
