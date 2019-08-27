#! /bin/bash
source ~/.bashrc
source /home/python/.virtualenvs/toutiao/bin/activate
export FLASK_ENV=production
cd /home/python/toutiao-backend/im/
exec python main.py 8090