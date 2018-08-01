## Prerequisites

*   Python 3

*   The pip package management tool

*   Other requirements:
    ```
    pip install -r requirements.txt

* https://developers.google.com/youtube/v3/getting-started

## Migrate Database
*   Add application to path:
    ```
    pip install -e .
*   Genererate migration script:
    ```
    alembic revision --autogenerate -m "migration msg"
*   Migrate database:
    ```
    alembic upgrade head

## FAQ (assumed)

Q: What are missed videos (and tests)? <br/>
A: Wiki: [Internal](https://git.vpn/BluABK/sane-yt-subfeed/wikis/Missed-videos-(and-tests)) / [External](https://git.blucoders.net/BluABK/sane-yt-subfeed/wikis/Missed-videos-(and-tests))