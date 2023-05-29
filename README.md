# Tutorial-chapter_4-MonteCarlo
This is Monte Carlo simulation part of Chapter 4.

## Main Objective
- Gain an understanding of the Monte Carlo analysis using an integrated HV-LV network model
- The simulation will be run multiple times. Each time a different customer phase connection, load, PV profiles, load allocation, and PV allocation are set
- The box-plots of each penetration level and transformers, lines, and customer attributes will be plotted at last.


## Pre-Requisites
- Basic familiarity with OpenDSS, Python 3 (Spyder or other IDE), and Jupyter Notebook (comes with Anaconda). GitHub Desktop is optional. [Download links and more info](https://sites.google.com/view/luisfochoa/research-tools).
- You should have completed all the [OpenDSS training material](https://sites.google.com/view/luisfochoa/research-tools/opendss-training-material).
- The tutorial with the name of  <a href="https://github.com/Team-Nando-Training/Tutorial-chapter_4"> Tutorial-chapter_4 </a>is recommended to study first. It is based on the same integrated HV-LV network model as Tutorial-chapter_4-MonteCarlo. The explanation of network building is at Tutorial-chapter_4.
- Note that in this tutorial we will not use the COM interface. Instead, we will use the dss_python module, a built-in Python library. [Training repo for dss_python](https://github.com/Team-Nando-Training/Tutorial-dss_python).
- **Nbextensions** needs to be installed too. It is an unofficial Jupyter Notebook extension package to provide various functions: automatic headings, contents and variable explorer, etc. Here is the [installation guide](https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html) for Nbextensions. You can simply follow these steps using the terminal:
1. pip install jupyter_contrib_nbextensions
2. jupyter contrib nbextension install --user
3. pip install jupyter_nbextensions_configurator
4. jupyter nbextensions_configurator enable --user  

## Run the Tutorial  
### Download project files from Github
- Download the source code (the .zip file will do) from the [releases section](https://github.com/Team-Nando-Training/Tutorial-chapter_4-MonteCarlo)(the releases section is not ready right now) or clone the entire repository to your local drive using GitHub Desktop. Unzip the file. It is important to place all the unzipped files in the same folder.
- Here is the explantaion of the files of this project  
 `Chapter4_MonteCarlo.ipynb` - the main Jupyter file including executing code and explanations.  
 The files included in the Network_txtfiles folder:   
 `Master.txt`, `source.txt`, `linecodes.txt`, `hv-line.txt`, `hv-transformer.txt`, `lv-transformer.txt`,`lv-line.txt`, `load.txt`,`loadshape.txt`- the OpenDSS commands including networking configuration.    
The python version and explanations of these commands are shown in another tutorial with the name of Tutorial-chapter_4. By using these txt files, the total calculation time will be saved.
`Simulation_results_of_different_Num_Run.docx` shows show the comparison of 30, 100, and 200 times simulation results. The number of simulation is a key factor of Monte Carlo simulation.   
The other files are introduced in Tutorial-chapter_4

### Execute the .ipynb file
- Open **Anaconda Prompt** and type "jupyter notebook --notebook-dir=`your address stored this project`". For example, jupyter notebook --notebook-dir=C:\OpenDSS
- Jupyter notebook will be opened in your browse. Click `Chapter4_MonteCarlo.ipynb`, it will appear on a new tab.
- Now you can explore the tutorial by running each cell accordingly (click on the **play button** on the left). Just bear in mind that the variable values are stored, so you need to clear all the outputs manually every time you want to intiate the whole program. Go to the Jupyter Notebook menu on top, select **Kernel** and then **Restart & Clear Output**.

## Credits
### This Repo and Adaptations to the Original Python Code
Angela Simonovska (asimonovska@student.unimelb.edu.au)  
Yushan Hou (yushou@student.unimelb.edu.au)  
Jing Zhu (jinzhu5@unimelb.edu.au)  
Muhammad Zulqarnain Zeb (m.zeb@unimelb.edu.au)  
Nando Ochoa (luis.ochoa@unimelb.edu.au)

### Original Python Code
Andreas Procopiou (andreasprocopiou@ieee.org)


 
