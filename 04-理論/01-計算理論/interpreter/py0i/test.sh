set -x

python3 py/fact.py
python3 py0i.py py/fact.py
python3 py0i.py py0i.py py/fact.py
python3 py0i.py py0i.py py/hello.py