# File/Folder Auto-sorter

Monitor any folder and sort your files and folders inside it automatically

## Methodology

1. Sort files based on extension as defined in the `config.json`
2. Sort folders based on maximum type of extensions present in the folder

## Usage

1. Install python 3.X
2. Create virtualenv:
```bash
    python -m venv env
```
3. Activate the environment:
    - Linux:
    ```bash
        source env/bin/activate 
    ```
    - Windows:
    ```bash
        env\\Scripts\\activate
    ```
4. Install requirements:
```bash
    pip install -r requirements.txt
```
5. Defining `config.json`:
    - Structure
    ```json
        {
            "include": {
                "extension-name": "path/to/folder/for/extension"
            },
            "ignore": ["extension-name"],
            "others": "path/to/misc/folder"
        }
    ```
    - Example
    ```json
        {
            "include": {
                "exe": "C:\\Users\\Username\\Downloads\\Software"
            },
            "ignore": ["tmp", "crdownload"],
            "others": "C:\\Users\\Username\\Downloads\\MISC"
        }
    ```
    > **Note**: Not having "others" in configuration will give you errors if that extension file is not defined in the config already.
    > The folders defined for every extension will be created automatically.
    > Configuration can be modified during runtime, it is loaded everytime a file is detected (can lead to performance issues for a large batch).
6. Run the script:
```bash
    python monitor.py "path/to/folder/to/monitor"
```