# Python API

## Installation

1. Download and install Python
    https://www.python.org/downloads/
    Must be Python 3
    It will install pip(python package manager) as well.

2. Install Python Package    
    ```sh
    pip install flask
    pip install flask-restful
    pip install flask-cors
    pip install requests
    ```

3. Create Database Schema(sqlite3)
   (This step not required if you download api.db as well)
    ```sh
    cd <Project folder>
    python schema.py
    ```

4. Run Api
    ```sh
    python api.py
    ```
