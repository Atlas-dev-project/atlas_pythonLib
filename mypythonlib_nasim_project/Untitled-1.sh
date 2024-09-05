



conda create --name myenv python=3.9
conda activate myenv


pip install --force-reinstall numpy==1.22.4
pip install --force-reinstall thinc==8.2.5
pip install --force-reinstall transformers

pip install torch
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/nightly/cpu

pip install accelerate

cd ~/llama
bash download.sh




cd /Users/straightup/Meta-Llama-3.1-8B

ls original/
curl -O https://huggingface.co/Meta-Llama-3.1-8B/resolve/main/original/config.json


python3 /Users/straightup/install_llama3b.py


huggingface-cli download meta-llama/Meta-Llama-3.1-8B --include "original/*" --local-dir Meta-Llama-3.1-8B