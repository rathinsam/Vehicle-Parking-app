This guide provides step-by-step instructions to set up and run a Vue2JS and Flask-based application with Celery, Redis, and a virtual environment in WSL.

Prerequisites:
Ensure that you have the following installed:
   WSL with Ubuntu (Refer to the installation guide if needed)   
   Python 3 and pip
   Redis

Step 1: Create and Activate Virtual Environment
   mkdir my_project && cd my_project
   python3 -m venv venv
   source venv/bin/activate

Step 2: Install Dependencies
   pip install -r requirements.txt

Step 3: Start Redis Server
   sudo service redis-server start

Step 4: Start Celery Worker
   celery -A app.celery beat --loglevel=info

Step 5: Start Celery Beat
   celery -A app.celery beat --loglevel=info

Step 6: Start Flask Application
   python app.py

Step 7: Testing the Setup
  cd frontend 
  python -m http.server
  
   
   
