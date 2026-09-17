cd src
./venv_setup_linux.sh > ../logs/installation.log
cd ..
source src/.venv/bin/activate
uvx hf auth login
