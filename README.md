<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/app_preview.png" alt="drawing" width="800px"/>

## Compatibility
This code is primarily tested on the following platforms:
*   Windows 10,     Python 3.7.0 with PyQt 5.11 (x64)
*   Linux/Debian 9, Python 3.5.3 with PyQt 5.10 (x64)
*   Arch,           Python 3.7.0 with PyQt 5.11 (x64)

### Known incompatibilities
#### x86 versions of Python
There's currently issues with memory leaks that leads to memory use above x86 python limit, causing it to crash. 

## Prerequisites

*   Python 3 (3.5+ is recommended)
*   The pip package management tool

Other requirements:

Python 3.6 and above:

    pip install -r requirements.txt
    
Python 3.5 and below: 

    pip install -r requirements-py35.txt


### Set up OAuth and API keys (pick _one_ option)
OAuth is required for access to your own youtube account (like retrieving subscriptions list). 
For anything else API keys is usually what gets used.

#### Option A: Use public/pre-made
Caution: This option is prone to daily API quota limit issues, option B is highly encouraged.
1. Rename `sane_yt_subfeed/resources/keys_public.json` to `keys.json`
2. Rename `sane_yt_subfeed/resources/client_secret_public.json` to `client_secret.json`

#### Option B: Set up your own
Useful ref: https://developers.google.com/youtube/v3/getting-started

  Go to https://console.developers.google.com/apis/dashboard and follow these steps:
  1. Click the drop-down next to the "Google APIs" logo in the banner area (upper left corner).
  2. Click "New Project".
  3. Fill in forms and create.
  4. Click the (presumably blue) "Enable APIs and services" text.
  5. Search for, and select "YouTube Data API v3"
  6. Enable "YouTube Data API v3"
  7. Go to "Credentials" screen
  
  1<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/01_open_project_dialog.png" alt="drawing" width="100px"/> 2<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/02_create_new_project.png" alt="drawing" width="100px"/> 3<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/03_name_and_create_project.png" alt="drawing" width="100px"/> 4<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/04_enable_api.png" alt="drawing" width="100px"/> 5<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/05_select_youtube_data_v3_api.png" alt="drawing" width="100px"/> 6<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/06_enable_youtube_data_v3_api.png" alt="drawing" width="100px"/> 7<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/07_go_to_credentials_screen.png" alt="drawing" width="100px"/>
  
  
  8. Create an API Key and copy the key into `sane_yt_subfeed/resources/keys.json.sample` and rename it `keys.json`
     
     8<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/08_create_api_key.png" alt="drawing" width="100px"/>
     
  9. Create an OAuth Client ID
     1. Configure consent screen, usage type is "other".
     2. Download json and save it as `sane_yt_subfeed/resources/client_secret.json` 
     
     9<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/09a_create_oauth_client.png" alt="drawing" width="100px"/> i<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/09b_configure_oauth_consent.png" alt="drawing" width="100px"/> ii<img src="https://github.com/BluABK/sane-subfeed/raw/master/docs/readme_assets/09c_create_oauth_client.png" alt="drawing" width="100px"/>
     
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

## Notable Wiki articles
*  [Missed videos and tests](https://github.com/BluABK/sane-subfeed/wiki/Missed-videos-(and-tests))
*  [Youtube-DL Integration (and overriding the youtube_dl options)](https://github.com/BluABK/sane-subfeed/wiki/YouTube-DL-integration)
