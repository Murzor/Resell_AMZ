"""
Worker RQ pour exécuter les tâches en arrière-plan.
Usage: rq worker --url redis://redis:6379/0 default
"""
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rq import Worker, Queue, Connection
from redis import Redis
from app.core.config import settings

if __name__ == "__main__":
    redis_conn = Redis.from_url(settings.REDIS_URL)
    
    with Connection(redis_conn):
        worker = Worker(Queue("default"))
        worker.work()

