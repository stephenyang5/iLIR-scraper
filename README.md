**Overview**
This repository contains functions that form a pipleine to collect data about AIM motifs of heterodera schactii. 
It does this by automatically sending fasta file queries to https://ilir.warwick.ac.uk/search.php. The script then records the output page of the website and converts it back into two sheets for anchor points and motifs.

I have two versions of the file, single.py and distributed.py. 
single.py is the only one in working condition currently. 
I am working on taking advantage of multiple threads to speed up the web scraping process. 
I need to implement locking on the output csv files such that threads are not 
overwriting each other.

**The pipeline works using the following functions:**

1. extract_fasta() - converts input data.csv into individual fasta files for each effector and saves them into in the data directory.
In distributed.py I create a series of subfolders such that multiple threads running send_batch() can operate on different data buckets to avoid concurrency problems. 

2. send_batch() - submits every fasta file in the input folder to the website query fields,
and then saves the results page as an html file in the web_data folder

3. read_table_files() - parses every saved html file in the inputted folder to find the query table and the anchor table within the website content, then adds the data into query_data.csv and anchor_data.csv in the output folder. It does this using helper functions
read_query_table() and read_anchor_table() to specifically parse data for the respective tables.

4. setup() - sets up the folder structure needed for this pipeline

5. cleanup() - deletes files and file structure generated from previous pipeline runs

Refer to the individual files for more in detail commenting

Please email stephen_c_yang@brown.edu if you have any questions or suggestions!

Stephen Yang
1/10/2025