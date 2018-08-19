<img src="https://img.bluabk.net/python_2018-07-28_19-10-08.png" alt="drawing" width="800px"/>

## Prerequisites

*   Python 3
*   The pip package management tool
*   Other requirements:
    ```
    pip install -r requirements.txt

### Set up OAuth and API keys (pick _one_ option)
OAuth is required for access to your own youtube account (like retrieving subscriptions list). 
For anything else API keys is usually what gets used.

#### Option A: Use public/pre-made
Caution: This option is prone to daily API quota limit issues, option B is highly encouraged.
1. Rename `sane_yt_subfeed/resources/keys_public.json` to `keys.json`
2. Rename `sane_yt_subfeed/resources/client_secret_public.json` to `client_secret.json`

#### Option B: Set up your own
Useful ref: https://developers.google.com/youtube/v3/getting-started

1. https://console.developers.google.com/apis/dashboard
2. Click the drop-down next to the "Google APIs" logo in the banner area.
3. Click "New Project".
4. Fill in forms and create.
5. Click the (presumably blue) "Enable APIs and services" text.
6. Search for, select and enable "YouTube Data API v3"
7. Go to "Credentials" and create credentials
8a. Create API Key
8b. Copy the key into `sane_yt_subfeed/resources/keys.json.sample` and rename it `keys.json`
9a. Create OAuth Client ID
9b. Configure consent screen, usage type is "other".
9c. Download json and save it as `sane_yt_subfeed/resources/client_secret.json` 

### Running the application
If it's the first time run: `pip install -e .` (required for non-Windows OS due to a pesky python path bug) <br/>

Afterwards you can launch it with: `python -m sane_yt_subfeed`

## Misc fixes and workarounds

### Migrate Database (if required to)
*   Add application to path (run it again, even if you've run it in the past):
    ```
    pip install -e .
    ```
    
*   Generate migration script:
    ```
    alembic revision --autogenerate -m "migration msg"
    ```
    
*   Migrate database:
    ```
    alembic upgrade head
    ```

## FAQ

Q: What are missed videos (and tests)? <br/>
A: Wiki: [Internal](https://git.vpn/BluABK/sane-yt-subfeed/wikis/Missed-videos-(and-tests)) / [External](https://git.blucoders.net/BluABK/sane-yt-subfeed/wikis/Missed-videos-(and-tests))