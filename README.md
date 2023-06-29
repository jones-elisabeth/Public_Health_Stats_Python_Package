# Public_Health_Stats_Python_Package

## Stats Package Instruction Manual

### Setup
#### Prerequisites
In order to get started with the stats package you need to have python and jupyter notebooks set up on your computer. Follow the instructions under “initial setup” here if you don’t already have those installed. 
#### Installing the Stats Package
Close any open jupyter notebooks, open terminals, and anaconda
Open your terminal on your desktop (cmd+space, type “terminal”)
Copy and paste the following in the terminal and press enter: 
pip install "git+https://github.com/ejones-rescue/Stats_Package.git"
If it was installed correctly it will say “Successfully installed Stats-Package” at the end of the load
If it asks you if you want to install any dependencies type Y and enter to continue
If you get any other errors during installation reach out to Elisabeth
#### Importing the Stats Packages to python
Every time you create a new python file that you want to use the Stats Packages in you need to import them using these two lines of code (copy and paste into your code):
from Stats_Package.stats_descriptives_module import freqs, desc, desc_subcats, xtab_cols, xtab_rows, xtab_all 
from Stats_Package.stats_analysis_module import chi_sq, chisq_posthoc_bon, ttest_1sample, ttest_2sample, ttest_paired, KW_shape_assumption, corr_pearson
Import pandas as pd
Import numpy as np
#### Before you get started
Before you get started on using the stats package there are a few essential python things to know, information is listed below but there is also example python code and base templates that can help you in this folder. 
Reading in your data file
In order to read in you data file to python you will need to copy, edit, and run the following code:
df = pd.read_excel(‘name of your file.xlsx’) 
If your file is in excel format and located in the folder you're working out of
df = pd.read_csv(‘name of your file.csv’)
If your file is in csv format and located in the folder you're working out of

