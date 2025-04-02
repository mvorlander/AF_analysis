
**README**

This notebook is a tool to annotate AF peak-vs-iptm plots and adds functionality to merge with external data and map the color, size, and transparency to arbitrary columns. The script can load annotations of the proteins from EBIs Complex portal (https://www.ebi.ac.uk/complexportal/home) for additional annotation.  You can also label points by lasso-selecting, text box search, index matching, or by Complex.

1.  **Create the environment:**
    
    ```bash
    conda env create -f environment.yml
    ```
    
2.  **Activate the environment:**
    
    ```bash
    conda activate my_notebook_env
    ```
    
3.  **Install the Jupyter kernel:**
    
    ```bash
    python -m ipykernel install --user --name my_notebook_env --display-name "My Notebook Env"
    ```
    
4.  **Launch Jupyter Notebook or JupyterLab and select the "My Notebook Env" kernel.**
    
