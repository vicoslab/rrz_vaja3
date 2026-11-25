# Vaja 3: Robotski manipulator

Glej [RRZ_vaja3.pdf](RRZ_vaja3.pdf).

## Namestitev

Predpogoji: Python 3.12+, git.

### Ubuntu

On Ubuntu, install the venv module first (other distros include it):

```bash
git clone https://github.com/vicoslab/rrz_vaja3.git
cd rrz_vaja3
sudo apt install python3-venv

#Virtualno okolje
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#USB Serial permissions
sudo usermod -aG dialout $USER
```

### Windows

```bat
git clone https://github.com/vicoslab/rrz_vaja3.git
cd rrz_vaja3
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```