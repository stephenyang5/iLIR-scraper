import os
import pandas as pd

def extract_fasta():
    if not os.path.exists('data'):
        os.mkdir('data')  # create a directory to store the fasta files
    # read data from csv
    df = pd.read_csv('data.csv')
    output = df.iloc[:, [0, 17]]  # select columns 0 and 8 (gene name and AA seq)


    counter = 0
    result = []
    for row in range(output.shape[0]):  
        name = '> ' + str(output.iloc[row,0]) + '\n'
        aa_seq = str(output.iloc[row,1]) + '\n'
        result.append(f"{name}{aa_seq}")

    with open ("fasta_files.txt", "w") as f:
        f.writelines(result) 

def filter_anchor(textfile):
    # Load the main data file
    df = pd.read_csv('data.csv')
    
    # Filter rows based on "Effector family" values
    filtered_families = df[(df["Effector family"].str.strip() == 'GLAND4-32e03-1106-3e10-6e07-10ao7') |
                           (df["Effector family"].str.strip() == '448 - 4d06')]
    
    # Extract relevant columns ("Gene ID" and "Effector family") for merging
    filtered_families = filtered_families[["Gene ID", "Effector family"]]
    
    # Load the target textfile
    df_text = pd.read_csv(textfile)
    
    # Merge the DataFrames based on the "Gene ID" (from data.csv) and "Id" (from textfile)
    merged_df = pd.merge(df_text, filtered_families, left_on="Id", right_on="Gene ID", how="inner")
    
    # Reorder columns to Effector family, Id, Value
    reordered_df = merged_df[["Effector family", "Id", "Start", "End", "Gene ID"]]
    output_df = reordered_df.iloc[:,:4]
    # Generate the output filename
    base_name = os.path.basename(textfile).split('_')[0]
    output_filename = f"filtered_{base_name}.csv"
    
    # Save the reordered DataFrame to a new file
    output_df.to_csv(output_filename, index=False)
    print(f"Filtered data with reordered columns saved to {output_filename}")
    
def filter_query(textfile):
    # Load the main data file
    df = pd.read_csv('data.csv')
    
    # Filter rows based on "Effector family" values
    filtered_families = df[(df["Effector family"].str.strip() == 'GLAND4-32e03-1106-3e10-6e07-10ao7') |
                           (df["Effector family"].str.strip() == '448 - 4d06')]
    
    # Extract relevant columns ("Gene ID" and "Effector family") for merging
    filtered_families = filtered_families[["Gene ID", "Effector family"]]
    
    # Load the target textfile
    df_text = pd.read_csv(textfile)
    
    # Merge the DataFrames based on the "Gene ID" (from data.csv) and "Id" (from textfile)
    merged_df = pd.merge(df_text, filtered_families, left_on="Id", right_on="Gene ID")
    
    # Reorder columns to Effector family, Id, Value
    reordered_df = merged_df[["Effector family", "Id", "Motif","Start","End","Pattern","PSSM Score","LIR in Anchor"]]
    # Generate the output filename
    base_name = os.path.basename(textfile).split('_')[0]
    output_filename = f"filtered_{base_name}.csv"
    
    # Save the reordered DataFrame to a new file
    reordered_df.to_csv(output_filename, index=False)
    print(f"Filtered data with reordered columns saved to {output_filename}")


filter_anchor('output/anchor_data.csv')
filter_query('output/query_data.csv')
