# Onet Email Generator

Script to automate email generating process on onet.pl domain. 
In order for everything to work properly, two things are needed:

1. **Proxy**

2. **[Capsolver](https://www.capsolver.com/) API key with balance**

## Preparing the Tool

Before you run main.py, follow these steps:

1. **Add Proxies to the proxies.txt**

2. **Insert Capsolver API Key in the key.json**

## Setting Up the Development Environment

To create a virtual environment (venv) and install the required dependencies, follow these steps:

1. Create a new virtual environment (venv):

    ```
    python -m venv venv
    ```

2. Activate the virtual environment:

   ```
   venv\Scripts\activate
   ```

3. Install the required dependencies from the `requirements.txt` file:

    ```
    pip install -r requirements.txt
    ```

## Fill onet.csv File

Fill in `onet.csv` which is located in the `data` folder. Make sure that the password passes validation and everything is filled out.

## Run script

When everything is filled out, run the script by executing `python main.py` while in the project's root directory. When everything is created correctly, a webhook will be sent to the url provided in the csv file and the data will be saved to `created_accounts.csv` in the `data` folder
