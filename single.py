# for interacting with iLIR query website
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  

import pandas as pd
import os
from bs4 import BeautifulSoup
import time

# this function extracts desired data out of an input data.csv file and writes it to fasta files
def extract_fasta():
    if not os.path.exists('data'):
        os.mkdir('data')  # create a directory to store the fasta files
    # read data from csv
    df = pd.read_csv('data.csv')
    output = df.iloc[:, [0, 8]]  # select columns 0 and 8 (gene name and AA seq)

    #check to validate output
    #output.to_csv('intermediate.csv')

    #2d loop through rows/cols
    counter = 0

    for row in range(output.shape[0]):  
        result = []
        result.append('> ' + str(output.iloc[row, 0]) )
        result.append(str(output.iloc[row, 1]))  # Convert to string

        with open(f"data/{str(output.iloc[row,0])}.fasta" , 'w') as h:
            h.write('\n'.join(result))
        counter +=1

# this function sends the fasta files to the iLIR website and saves the results
def send_batch(folder):
    #dirs
    fasta_directory = folder
    results_directory = "web_data"
    submission_url = "https://ilir.warwick.ac.uk/search.php"

    # configure selenium webdriver
    options = Options()
    options.add_argument('--headless')

      # Set to True to hide the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    counter = 0
    #loop through fasta files
    for fasta_file in os.listdir(fasta_directory):
        if fasta_file.endswith(".fasta"):  # Process only .fasta files
            file_path = os.path.join(fasta_directory, fasta_file)
            
            # read the content of the FASTA file
            with open(file_path, 'r') as file:
                fasta_content = file.read()
                print(f"Submitting {fasta_file}...")

            #use selenium to submit the fasta file
            driver.get(submission_url)
            
            input_element = driver.find_element(By.NAME, "input")
            input_element.send_keys(fasta_content)
            
            submit_button = driver.find_element(By.NAME, "SUBMIT")
            submit_button.click()


            main_window = driver.current_window_handle  
            all_windows = driver.window_handles 

            for window in all_windows:
                if window != main_window:
                    driver.switch_to.window(window) 
                    break

            #wait until webpage is fully loaded then save information
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            #save results to intermediate directory
            result_file_path = os.path.join(results_directory, f"{fasta_file.split('.')[0]}_result.html")
            with open(result_file_path, 'w', encoding='utf-8') as result_file:
                result_file.write(driver.page_source)
            counter+=1
            driver.close()
            driver.switch_to.window(main_window)
   
    # Quit the driver
    driver.quit()
    return counter

# this function reads the output of the iLIR website queries and converts them to csv
def read_query_table(soup, id):
    #find first table 
    query_table = soup.find_all('table')[0]
    query_rows = query_table.find_all('tr')[1:] 

    # add ordered data to list adding an id column
    query_data = []
    for row in query_rows:
        cols = row.find_all('td')
        if cols:  
            query_data.append([str(id)]+[col.text.strip() for col in cols])
    
    # append data to single file and write to csv
    query_df = pd.DataFrame(query_data, columns=["Id", "Motif", "Start", "End", "Pattern", "PSSM Score", "LIR in Anchor"])
    try:
        existing_df = pd.read_csv('output/query_data.csv')
        combined_df = pd.concat([existing_df, query_df], ignore_index=True)
    except FileNotFoundError:
        combined_df = query_df

    combined_df.to_csv('output/query_data.csv', index=False)

# this function reads the output of the iLIR website queries and converts them to csv
def read_anchor_table(soup, id):

    anchor_table = soup.find_all('table')[1]  # Second table
    anchor_rows = anchor_table.find_all('tr')[1:]  # Skip the header row

    anchor_data = []
    for row in anchor_rows:
        cols = row.find_all('td')
        if cols:
            anchor_data.append([str(id)]+[col.text.strip() for col in cols])

    anchor_df = pd.DataFrame(anchor_data, columns=["Id", "Anchor", "Start", "End"])
    try:
        existing_df = pd.read_csv('output/anchor_data.csv')
        combined_df = pd.concat([existing_df, anchor_df], ignore_index=True)
    except FileNotFoundError:
        combined_df = anchor_df

    combined_df.to_csv('output/anchor_data.csv', index=False)

# this function takes the output of all of the web queries and parse them to find tables and convert to csv
def read_table_files():
    try:
        os.remove('output/query_data.csv')
        os.remove('output/anchor_data.csv')
    except FileNotFoundError:
        pass

    counter = 0
    dir = 'web_data'
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)

        if os.path.isfile(file_path):
            # read file, check to see if there is an anchor table
            with open(file_path, 'r') as file:
                html_content = file.read()
                gene_name= os.path.basename(file_path).split('_result')[0]
                soup = BeautifulSoup(html_content, 'html.parser')
                tables = soup.findAll('table')
                print(f"Reading {gene_name} with {len(tables)} tables...")
                read_query_table(soup, gene_name)

                if len(tables) >= 2:
                    read_anchor_table(soup, gene_name)
                counter+=1
    print(f"Processed {counter} files.")

def cleanup():
    # Specify the directory path
    
    cleanup_folders = ["data", "web_data"]
    for folder in cleanup_folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                
                # Check if it is a file (not a subdirectory) and delete it
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                else:
                    print(f"Skipped: {file_path} (not a file)")
            try:
                os.rmdir(folder)
                print(f"Deleted folder: {folder}")
            except OSError as e:
                print(f"Error deleting deleting {folder} because of {e}")
        else:
            print(f"The directory {folder} does not exist.")

def setup():
    
    os.mkdir("data")
    
    os.mkdir("web_data")

    try:
        os.mkdir("output")
    except FileExistsError:
        pass



# Define the function that processes a folder
def process_folder(folder_path):
    # Simulate data processing
    print(f"Processing folder: {folder_path}")
    # Your code to submit data to the website and record results
    # Example: submit_to_website(folder_path)
    return f"Completed {folder_path}"




def main():
    start_time = time.time()
    cleanup()
    setup()
    extract_fasta()
    num_files = send_batch("data")

    end_time = time.time()

    read_table_files()
    print(f"program took {end_time-start_time:.2f} seconds to run and processed {num_files} files")


if __name__ == "__main__":
    main()