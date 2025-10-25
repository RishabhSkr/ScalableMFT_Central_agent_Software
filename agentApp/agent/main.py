# agent/main.py
import time
import sys
import signal
from pathlib import Path
from datetime import datetime
import threading

from agent.config import AgentConfig
from agent.core.scheduler import TaskScheduler
from agent.core.heartbeat import HeartbeatSender
from agent.communication.api_client import CentralAPIClient
from agent.utils.logger import setup_logger

logger = setup_logger()

class FTPTransferAgent:
    def __init__(self):
        self.config = AgentConfig()
        self.running = False
        self.api_client = CentralAPIClient(
            base_url=self.config.central_server_url,
            agent_id=self.config.agent_id
        )
        self.scheduler = TaskScheduler(self.api_client, self.config)
        self.heartbeat = HeartbeatSender(self.api_client, self.config)
        
    def start(self):
        """Start the agent"""
        logger.info("Starting FTP Transfer Agent...")
        logger.info(f"Agent ID: {self.config.agent_id}")
        logger.info(f"Central Server: {self.config.central_server_url}")
        
        # Register with central server
        if not self.register():
            logger.error("Failed to register with central server. Exiting.")
            return
        
        self.running = True
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        # Start main task loop
        self._task_loop()
    
    def register(self) -> bool:
        """Register agent with central server"""
        try:
            from agent.utils.system_info import get_system_info
            system_info = get_system_info()
            
            response = self.api_client.register_agent(system_info)
            
            if response:
                logger.info("Successfully registered with central server")
                # Get and save access token
                token_response = self.api_client.get_access_token()
                if token_response:
                    self.config.save_token(token_response['access_token'])
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False
    
    def _heartbeat_loop(self):
        """Send periodic heartbeats to central server"""
        while self.running:
            try:
                self.heartbeat.send()
                time.sleep(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                time.sleep(30)  # Retry after 30 seconds
    
    def _task_loop(self):
        """Main task execution loop"""
        logger.info("Agent is now running. Checking for tasks...")
        
        while self.running:
            try:
                # Fetch pending tasks from central server
                tasks = self.api_client.get_pending_tasks()
                
                if tasks:
                    logger.info(f"Received {len(tasks)} task(s) to execute")
                    
                    for task in tasks:
                        self.scheduler.execute_task(task)
                
                # Wait before next check
                time.sleep(self.config.task_check_interval)
            
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.stop()
                break
            
            except Exception as e:
                logger.error(f"Task loop error: {e}")
                time.sleep(60)  # Wait before retrying
    
    def stop(self):
        """Stop the agent gracefully"""
        logger.info("Stopping FTP Transfer Agent...")
        self.running = False
        time.sleep(2)
        logger.info("Agent stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    agent = FTPTransferAgent()
    agent.start()
