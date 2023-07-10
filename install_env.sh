#!/bin/bash

# This script installs a Mamba environment from an env.yml file

# Define the name of the environment
ENV_NAME=macss_grant

# Install the environment from the env.yml file
mamba env create --name $ENV_NAME --file env.yml

# Activate the environment
conda activate $ENV_NAME

# Verify that the environment was installed correctly
conda env list