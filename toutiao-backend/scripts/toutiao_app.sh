#! /bin/bash
source ~/.bash_profile
source /home/python/.virtualenvs/toutiao/bin/activate
export FLASK_ENV=production
cd /home/python/toutiao-backend
exec gunicorn -b 0.0.0.0:8000 --access-logfile /home/python/logs/access_app.log --error-logfile /home/python/logs/error_app.log toutiao.main:app
