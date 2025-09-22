1) for virtual-environment python -m venv venv 
  to activate source venv/bin/activate
  pip install -r requirements.txt
2) For redis to start run redis-server --port 6380
    if it exists then sudo pkill redis-server
3) For celery celery -A celery_worker.celery worker --beat --loglevel=info
    if it exists then rm celerybeat-schedule
4) to run app python3 app.py
5) for mail mailhog
6) to frontend run python3 -m http.server