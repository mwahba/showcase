# README
This is a showcase for my current projects and interests.

As of December 2024, my main interest is delving deeper into Machine Learning technologies and algorithms; understanding the underlying statistics and math that drive much of what we see in today's Artificial Intelligence boom (specifically as it relates to LLMs and Trading).

My experience has been mainly in full stack application technologies, with a heavy focus on efficiency of the code.

# Conda Environments
1. To establish the Conda environment: `conda env create --file=environment.yml`
1. To update the Conda environment: 
    11. `conda activate [environment_name]`
    11. `conda update --file=environment.yml --prune` to take in the changes and uninstall removed dependencies.
1. To run commands with sudo in a conda environment:
    11. `conda activate [environment_name]`
    11. `sudo $(which python) script_name.py`