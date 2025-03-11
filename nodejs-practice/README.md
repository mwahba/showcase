# Node.JS/Express Practice

## Instructions
1. To establish the Conda environment: `conda env create --file=environment.yml`
1. To update the Conda environment: 
    11. `conda activate nodejs_env`
    11. `conda env update --file=environment.yml --prune` to take in the changes and uninstall removed dependencies.
1. To run commands with sudo in a conda environment:
    11. `conda activate nodejs_env`
1. 

## Messaging App
1. Create a `.env` file with the following content, replacing with the appropriate configurations:
```
MONGODB_PORT = 27017
MONGODB_URI = mongodb://localhost:27017/messaging_app
REDIS_HOST = localhost
REDIS_PORT = 6379
JWT_SECRET = your_jwt_secret
PORT = 3000
```