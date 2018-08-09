<img src="https://img.bluabk.net/python_2018-07-28_19-10-08.png" alt="drawing" width="800px"/>
## Prerequisites

*   Python 3

*   The pip package management tool

*   Other requirements:
    ```
    pip install -r requirements.txt

* https://developers.google.com/youtube/v3/getting-started

## Migrate Database(for: sqlite3.OperationalError, when using old db)
*   Add application to path:
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

## FAQ (assumed)

Q: What are missed videos (and tests)? <br/>
A: Wiki: [Internal](https://git.vpn/BluABK/sane-yt-subfeed/wikis/Missed-videos-(and-tests)) / [External](https://git.blucoders.net/BluABK/sane-yt-subfeed/wikis/Missed-videos-(and-tests))