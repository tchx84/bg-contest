Sugar Background Image Contest
==============================

This is the web application for the contest.

Development
-----------

1. If you don't have virtualenv:

    sudo easy_install virtualenv

Or

    sudo pip install virtualenv

Or

    sudo apt-get install python-virtualenv

2. Create environment:

    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    mkdir media
    chmod a+rwx media

3. Start:

    python __init__.py

4. Serve media:

    cd media
    python -m SimpleHTTPServer
