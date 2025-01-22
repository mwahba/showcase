# Learning Machine Learning
This part of the repo documents my journey through learning some of the current machine learning methods, libraries, etc.

## Setup
### Install `pyenv`
#### Debian/Ubuntu
```
# Install dependencies, if needed
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git

# Install pyenv
curl https://pyenv.run | bash
```

#### Post-setup
To find your current shell, use `echo $SHELL`.

##### Bash
```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
```

##### ZSH
```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
source ~/.zshrc
```

### Install Python version
1. Find the latest or specific version of python you want to install using pyenv: `pyenv install -l | grep python3.12`
1. Use `pyenv install 3.12.8` (as an example).
1. Set to local version for specific project directory: `pyenv local 3.12.8`

### Use a Virtual Environment:
1. Create virtual environment (named py3.12): `pyenv virtualenv 3.12.8 py3.12`
1. Activate the virtual environment: `pyenv activate py3.12`

### Install Required Packages
1. Upgrade pip: `python -m pip install --upgrade pip`
1. Install required packages:
11. With a `requirements.txt` file: `pip install -r <path>/requirements.txt`, replacing `<path>` with the appropriate path.
11. With manual dependencies (e.g. `numpy pandas jupyter`): `pip install numpy pandas jupyter tensorflow[and-gpu] scikit-learn keras` (if you have specific versions you will have to specify them)
1. Validate Tensorflow GPU install: `python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`