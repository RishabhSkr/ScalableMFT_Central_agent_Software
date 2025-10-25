# agent/communication/rabbitmq_client.py
"""
Optional: Agent can also connect to RabbitMQ for push-based task assignment
instead of polling REST API
"""
import pika
import json
from typing import Callable

from agent.utils.logger import setup_logger

logger = setup_logger()

class AgentRabbitMQClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Connect to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"Agent connected to RabbitMQ at {self.host}:{self.port}")
        
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def subscribe_to_tasks(self, agent_id: str, callback: Callable):
        """Subscribe to task assignments for this agent"""
        queue_name = f"agent_{agent_id}_tasks"
        
        # Declare agent-specific queue
        self.channel.queue_declare(queue=queue_name, durable=True)
        
        # Bind to task assignment routing key
        self.channel.queue_bind(
            exchange='ftp_transfer_exchange',
            queue=queue_name,
            routing_key=f"task.assigned.{agent_id}"
        )
        
        # Start consuming
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False
        )
        
        logger.info(f"Subscribed to task queue: {queue_name}")
        self.channel.start_consuming()
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
