# app/workers/worker_launcher.py
"""
Launch different worker processes for consuming messages
"""
import sys
import argparse
from app.messaging.consumers import (
    TaskConsumer,
    AgentConsumer,
    LogConsumer,
    AlertConsumer
)
from app.utils.logger import setup_logger

logger = setup_logger()

def start_task_worker():
    """Start task processing worker"""
    logger.info("Starting Task Worker...")
    consumer = TaskConsumer()
    consumer.start()

def start_agent_worker():
    """Start agent processing worker"""
    logger.info("Starting Agent Worker...")
    consumer = AgentConsumer()
    consumer.start()

def start_log_worker():
    """Start log processing worker"""
    logger.info("Starting Log Worker...")
    consumer = LogConsumer()
    consumer.start()

def start_alert_worker():
    """Start alert processing worker"""
    logger.info("Starting Alert Worker...")
    consumer = AlertConsumer()
    consumer.start()

def main():
    parser = argparse.ArgumentParser(description='RabbitMQ Worker Launcher')
    parser.add_argument(
        'worker_type',
        choices=['task', 'agent', 'log', 'alert', 'all'],
        help='Type of worker to start'
    )
    
    args = parser.parse_args()
    
    if args.worker_type == 'task':
        start_task_worker()
    elif args.worker_type == 'agent':
        start_agent_worker()
    elif args.worker_type == 'log':
        start_log_worker()
    elif args.worker_type == 'alert':
        start_alert_worker()
    elif args.worker_type == 'all':
        # Start all workers in separate threads
        import threading
        
        workers = [
            threading.Thread(target=start_task_worker, daemon=True),
            threading.Thread(target=start_agent_worker, daemon=True),
            threading.Thread(target=start_log_worker, daemon=True),
            threading.Thread(target=start_alert_worker, daemon=True)
        ]
        
        for worker in workers:
            worker.start()
        
        # Keep main thread alive
        for worker in workers:
            worker.join()

if __name__ == '__main__':
    main()
