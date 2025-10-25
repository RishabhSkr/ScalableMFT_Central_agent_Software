# app/messaging/rabbitmq.py
import pika
import json
from typing import Callable, Dict, Any
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger()

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange_name = 'ftp_transfer_exchange'
        self.connect()
    
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
        
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def declare_queue(self, queue_name: str, routing_key: str):
        """Declare a queue and bind it to exchange"""
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        logger.info(f"Queue '{queue_name}' declared and bound to '{routing_key}'")
    
    def publish_message(self, routing_key: str, message: Dict[str, Any]):
        """Publish message to exchange"""
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            logger.debug(f"Published message to '{routing_key}': {message}")
        
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            # Reconnect and retry
            self.connect()
            self.publish_message(routing_key, message)
    
    def consume_messages(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ):
        """Start consuming messages from queue"""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=auto_ack
        )
        
        logger.info(f"Starting to consume messages from '{queue_name}'")
        self.channel.start_consuming()
    
    def close(self):
        """Close connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

# Singleton instance
rabbitmq_client = RabbitMQClient()
