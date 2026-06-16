## How to Start the Virtual Environment

If the environment is not locally installed, run:

```bash
python -m venv venv
```

After that, or if already installed, activate it:

**Mac/Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.\venv\Scripts\activate
```

After you enter the virtual enviornment, run:

```bash
pip install -r  .\requirements.txt
```

To run the updates, use this line in the virtual enviornment:

```bash
python.exe -m pip install --upgrade pip
```

To run the file, run in the terminal:

```bash
python .\main.py
```
