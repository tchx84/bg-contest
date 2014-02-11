Sugar Background Image Contest
==============================

This is the web application for the contest.

Development
-----------

- If you don't have virtualenv:

    ```
    sudo easy_install virtualenv
    ```

    Or
    ```
    sudo pip install virtualenv
    ```

    Or
    ```
    sudo apt-get install python-virtualenv
    ```

- Create environment:

    ```
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    mkdir media
    chmod a+rwx media
    ```

- Start:

    ```
    python __init__.py
    ```

- Serve media:

    ```
    cd media
    python -m SimpleHTTPServer
    ```
