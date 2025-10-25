# Complete Technology Stack Guide for Beginners

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack Explained](#technology-stack-explained)
3. [How Components Interact](#how-components-interact)
4. [Installation Guide](#installation-guide)
5. [Deployment Scripts](#deployment-scripts)
6. [Testing Guide](#testing-guide)

---

## System Overview

### What Does This System Do?

You're building a **centralized file transfer management system** that:
- Runs on **150 PCs** (agents) across your organization
- Each PC transfers **2GB of data per day** to an FTP server
- A **central server** manages, monitors, and coordinates all transfers
- Provides **real-time monitoring** and **automatic retry** on failures

### The Big Picture

Think of it like this:
- **150 Workers** (agent PCs) doing file transfers
- **1 Manager** (central server) coordinating everything
- **Message System** (RabbitMQ) for communication
- **Database** (PostgreSQL) for record keeping
- **Scheduler** (Celery) for timing tasks
- **Dashboard** (Web UI) for monitoring

---

## Technology Stack Explained

### 1. **Python** (Programming Language)

**What is it?**
- The programming language used to write both central server and agent software
- Easy to learn, powerful, and has great libraries for networking and automation

**Why use it?**
- Cross-platform (works on Windows, Linux, Mac)
- Rich ecosystem for FTP, networking, and web APIs
- Easy to deploy with tools like PyInstaller

**Where used in our system?**
- Agent software (runs on 150 PCs)
- Central server API and workers
- All automation scripts

---

### 2. **FastAPI** (Web Framework)

**What is it?**
- A modern Python web framework for building REST APIs
- Think of it as a way to create "endpoints" that agents can call over HTTP

**Why use it?**
- Super fast performance
- Automatic API documentation (Swagger UI)
- Easy input validation with Pydantic
- Built-in async support

**Example use case in our system:**
```
Agent calls: http://central-server:8000/api/agents/register
FastAPI handles the request and saves agent info to database
```

**API Endpoints we create:**
- `POST /api/agents/register` - Register new agent
- `POST /api/agents/{id}/heartbeat` - Agent check-in
- `GET /api/agents/{id}/tasks` - Get pending tasks
- `POST /api/logs/` - Submit transfer logs

---

### 3. **PostgreSQL** (Database)

**What is it?**
- A powerful, open-source relational database
- Stores all persistent data in tables with relationships

**Why use it?**
- ACID compliant (reliable transactions)
- Handles millions of records efficiently
- Supports complex queries and indexing
- Industry standard for production systems

**What data we store:**
- **agents table**: Info about all 150 PCs (hostname, IP, status, last heartbeat)
- **tasks table**: Transfer jobs (source, destination, schedule, status)
- **transfer_logs table**: History of all transfers (success/failure, duration, file size)
- **alerts table**: Notifications about failures or issues

**Example:**
```
agents table:
+----------+------------+-----------+--------+------------------+
| agent_id | hostname   | ip_addr   | status | last_heartbeat   |
+----------+------------+-----------+--------+------------------+
| uuid-001 | PC-PLANT-1 | 10.0.0.5  | active | 2025-10-21 10:35 |
| uuid-002 | PC-PLANT-2 | 10.0.0.6  | active | 2025-10-21 10:36 |
+----------+------------+-----------+--------+------------------+
```

---

### 4. **RabbitMQ** (Message Broker)

**What is it?**
- A message queue system that acts like a post office for your applications
- Allows different parts of your system to communicate asynchronously

**Why use it?**
- **Decoupling**: API server doesn't wait for slow operations
- **Reliability**: Messages are persisted, won't lose data if server restarts
- **Scalability**: Can add more workers to handle increased load
- **Load balancing**: Distributes work among multiple workers

**How it works (Simple analogy):**
```
1. Restaurant (API) takes order (request)
2. Puts ticket in queue (RabbitMQ)
3. Kitchen workers (Workers) pick up tickets and cook
4. Restaurant can take more orders without waiting
```

**Message Flow in our system:**

```
Event: Agent completes file transfer
↓
API receives log → Publishes to "transfer_logs" queue
↓
Log Worker picks up message → Processes log → Updates database
↓
Task Worker sees completion → Updates task status → Triggers next action
```

**Key Concepts:**

- **Producer**: Sends messages (our FastAPI app)
- **Queue**: Holds messages waiting to be processed
- **Consumer**: Receives and processes messages (our workers)
- **Exchange**: Routes messages to appropriate queues
- **Routing Key**: Determines which queue gets the message

**Our Queues:**
- `task_assignment_queue` - New tasks for agents
- `task_completion_queue` - Completed/failed transfer notifications
- `agent_heartbeat_queue` - Agent status updates
- `transfer_logs_queue` - Transfer result logs
- `alerts_queue` - Critical alerts and notifications

---

### 5. **Redis** (In-Memory Cache)

**What is it?**
- Super-fast in-memory data store
- Used as Celery's message broker and result backend

**Why use it?**
- Extremely fast (microsecond latency)
- Supports various data structures (lists, sets, sorted sets)
- Simple to setup and use

**In our system:**
- Celery uses it to store task queues
- Stores scheduled task information
- Can cache frequently accessed data

---

### 6. **Celery** (Task Queue / Scheduler)

**What is it?**
- A distributed task queue system for Python
- Allows you to run tasks in the background or on a schedule

**Why use it?**
- Run time-consuming tasks asynchronously
- Schedule periodic tasks (like cron jobs)
- Retry failed tasks automatically
- Distribute work across multiple machines

**Use cases in our system:**

**Periodic Tasks (like cron):**
```python
# Check agent health every 60 seconds
@celery_app.task
def check_agent_heartbeats():
    # Find agents that haven't checked in for 5+ minutes
    # Mark them as offline
    # Send alerts
```

**Scheduled Jobs:**
- Every 30 seconds: Check for pending tasks and assign to agents
- Every 1 minute: Monitor agent heartbeats
- Every 5 minutes: Retry failed tasks
- Every day: Generate summary reports

**Celery Beat:**
- The scheduler component
- Like a cron daemon that triggers tasks on schedule

---

### 7. **Docker & Docker Compose** (Containerization)

**What is it?**
- Docker: Packages applications with all dependencies into "containers"
- Docker Compose: Runs multiple containers together as a system

**Why use it?**
- **Consistency**: Same environment everywhere (dev, test, production)
- **Isolation**: Each service runs in its own container
- **Easy deployment**: One command starts everything
- **Portability**: Works on any system with Docker

**Our Docker Setup:**
```
docker-compose.yml defines:
- PostgreSQL container
- Redis container
- RabbitMQ container
- FastAPI application container
- 4 RabbitMQ worker containers
- 2 Celery worker containers
```

**Benefits:**
```bash
# Start entire system with one command
docker-compose up -d

# Stop entire system
docker-compose down

# View logs
docker-compose logs -f
```

---

### 8. **SQLAlchemy** (ORM - Object Relational Mapper)

**What is it?**
- Python library that lets you work with databases using Python objects instead of SQL

**Example:**
```python
# Without ORM (raw SQL)
cursor.execute("INSERT INTO agents (hostname, ip_address) VALUES ('PC-1', '10.0.0.5')")

# With SQLAlchemy ORM
new_agent = Agent(hostname='PC-1', ip_address='10.0.0.5')
db.add(new_agent)
db.commit()
```

**Benefits:**
- Type-safe queries
- Automatic relationship handling
- Database migration support (Alembic)
- Protection against SQL injection

---

### 9. **Pydantic** (Data Validation)

**What is it?**
- Library for data validation using Python type hints
- Automatically validates incoming API requests

**Example:**
```python
class AgentRegister(BaseModel):
    hostname: str
    ip_address: str
    agent_version: str

# FastAPI automatically validates
@app.post("/agents/register")
def register(agent: AgentRegister):
    # If data doesn't match model, returns 422 error automatically
    pass
```

---

### 10. **Paramiko** (SSH/SFTP Library)

**What is it?**
- Python library for SSH and SFTP connections
- Used by agents to securely upload files

**Why use it?**
- Secure file transfer (encryption)
- Supports key-based authentication
- Cross-platform

---

### 11. **Nginx** (Reverse Proxy / Load Balancer)

**What is it?**
- Web server that sits in front of your FastAPI application
- Handles SSL, load balancing, static files

**Why use it?**
- SSL/TLS termination (HTTPS)
- Load balancing across multiple API instances
- Serves static files (dashboard)
- Rate limiting and security

---

## How Components Interact

### Scenario 1: Agent Registration

```
Step 1: Agent starts up
↓
Step 2: Agent calls POST /api/agents/register
        - Sends: hostname, IP, OS info, version
↓
Step 3: FastAPI receives request
        - Validates data with Pydantic
        - Creates Agent record in PostgreSQL
        - Publishes "agent.registered" message to RabbitMQ
        - Returns agent_id and JWT token
↓
Step 4: Agent Worker consumes registration message
        - Can trigger welcome email
        - Initialize monitoring
        - Log event
↓
Step 5: Agent stores token and starts heartbeat loop
```

### Scenario 2: Task Execution Flow

```
Step 1: Admin creates task via dashboard
        POST /api/tasks/ {agent_id, source_path, destination}
↓
Step 2: FastAPI creates task in PostgreSQL
        - Status: 'pending'
        - Next run time: now
        - Publishes "task.assigned" to RabbitMQ
↓
Step 3: Agent polls GET /api/agents/{id}/tasks
        - Receives pending tasks
↓
Step 4: Agent executes task
        a. Compresses file (if enabled)
        b. Calculates checksum
        c. Connects to FTP server (SFTP/FTPS)
        d. Uploads file
        e. Verifies upload
↓
Step 5: Agent submits result POST /api/logs/
        - Task ID, status, checksum, duration, file size
↓
Step 6: FastAPI receives log
        - Saves to transfer_logs table
        - Publishes "task.completed" to RabbitMQ
↓
Step 7: Task Worker processes completion
        - Updates task status to 'completed'
        - Updates agent statistics
        - If failed: queues for retry
↓
Step 8: If failed, Alert Worker sends notification
        - Email to admin
        - Updates dashboard
```

### Scenario 3: Heartbeat Monitoring

```
Step 1: Celery Beat scheduler triggers every 60 seconds
↓
Step 2: Heartbeat Monitor Worker runs
        - Queries agents table
        - Finds agents with last_heartbeat > 5 minutes ago
↓
Step 3: For each inactive agent:
        - Updates status to 'inactive'
        - Publishes "agent.offline" to RabbitMQ
↓
Step 4: Alert Worker receives offline notification
        - Creates alert in database
        - Sends email to admin
        - Updates dashboard
```

### Scenario 4: Automatic Retry

```
Step 1: Transfer fails (network issue, FTP server down)
↓
Step 2: Agent logs failure
↓
Step 3: Task Worker sees failure
        - Checks retry_count < max_retries
        - Increments retry_count
        - Sets next_run_time = now + (5 * retry_count) minutes
        - Updates status to 'pending'
        - Publishes "task.retry" message
↓
Step 4: Agent picks up retry task on next poll
↓
Step 5: If still fails after max_retries:
        - Mark as 'failed'
        - Create critical alert
        - Wait for manual intervention
```

---

## Installation Guide

### Prerequisites

**On Central Server (Linux recommended):**
- Ubuntu 20.04+ or CentOS 8+
- 4 CPU cores minimum
- 8GB RAM minimum
- 100GB disk space
- Python 3.10+
- Docker & Docker Compose (recommended) OR individual services

**On Agent PCs (Windows):**
- Windows 10/11
- 2GB RAM minimum
- Python 3.10+
- Network access to central server and FTP server

### Step-by-Step Setup

#### Option A: Docker Setup (Recommended for Beginners)

**1. Install Docker and Docker Compose**

```bash
# On Ubuntu
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

**2. Clone or Create Project Structure**

```bash
mkdir ftp-transfer-system
cd ftp-transfer-system

# Create directory structure
mkdir -p app/api app/models app/schemas app/services app/workers app/messaging app/utils
mkdir -p agent/core agent/communication agent/utils agent/service
mkdir -p data logs
```

**3. Create Configuration Files**

Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://ftp_user:SecurePass123@postgres:5432/ftp_central

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=SecureRabbitPass123

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-very-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@yourcompany.com
```

**4. Create docker-compose.yml** (provided in previous response)

**5. Start the System**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Access services:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - RabbitMQ Management: http://localhost:15672 (guest/guest)
# - PostgreSQL: localhost:5432
```

**6. Initialize Database**

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Or create tables directly
docker-compose exec api python -c "from app.database import engine; from app.models import agent, task, transfer_log, alert; agent.Base.metadata.create_all(bind=engine); task.Base.metadata.create_all(bind=engine); transfer_log.Base.metadata.create_all(bind=engine); alert.Base.metadata.create_all(bind=engine)"
```

**7. Verify Installation**

```bash
# Check API health
curl http://localhost:8000/health

# Check RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview

# Check PostgreSQL
docker-compose exec postgres psql -U ftp_user -d ftp_central -c "SELECT version();"
```

---

#### Option B: Manual Setup (Without Docker)

**1. Install PostgreSQL**

```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE ftp_central;
CREATE USER ftp_user WITH PASSWORD 'SecurePass123';
GRANT ALL PRIVILEGES ON DATABASE ftp_central TO ftp_user;
\q
```

**2. Install RabbitMQ**

```bash
# Ubuntu
sudo apt install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Create admin user
sudo rabbitmqctl add_user admin SecureRabbitPass123
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

**3. Install Redis**

```bash
# Ubuntu
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**4. Install Python Dependencies**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**5. Configure Environment**

Create `.env` file with localhost URLs:
```
DATABASE_URL=postgresql://ftp_user:SecurePass123@localhost:5432/ftp_central
RABBITMQ_HOST=localhost
REDIS_URL=redis://localhost:6379/0
```

**6. Initialize Database**

```bash
# Create tables
python -c "from app.database import engine; from app.models import agent, task, transfer_log, alert; agent.Base.metadata.create_all(bind=engine); task.Base.metadata.create_all(bind=engine); transfer_log.Base.metadata.create_all(bind=engine); alert.Base.metadata.create_all(bind=engine)"
```

**7. Start Services Manually**

Open separate terminal windows for each:

```bash
# Terminal 1: FastAPI
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: RabbitMQ Task Worker
source venv/bin/activate
python -m app.workers.worker_launcher task

# Terminal 3: RabbitMQ Agent Worker
source venv/bin/activate
python -m app.workers.worker_launcher agent

# Terminal 4: RabbitMQ Log Worker
source venv/bin/activate
python -m app.workers.worker_launcher log

# Terminal 5: RabbitMQ Alert Worker
source venv/bin/activate
python -m app.workers.worker_launcher alert

# Terminal 6: Celery Worker
source venv/bin/activate
celery -A app.workers.task_scheduler worker --loglevel=info

# Terminal 7: Celery Beat
source venv/bin/activate
celery -A app.workers.task_scheduler beat --loglevel=info
```

---

## Deployment Scripts

### Production Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "=== FTP Transfer System Deployment ==="

# Configuration
PROJECT_DIR="/opt/ftp-transfer-system"
BACKUP_DIR="/opt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. Backup existing system
echo "Step 1: Creating backup..."
if [ -d "$PROJECT_DIR" ]; then
    mkdir -p $BACKUP_DIR
    tar -czf $BACKUP_DIR/ftp-system-$TIMESTAMP.tar.gz -C $PROJECT_DIR .
    print_success "Backup created: $BACKUP_DIR/ftp-system-$TIMESTAMP.tar.gz"
fi

# 2. Pull latest code
echo "Step 2: Pulling latest code..."
cd $PROJECT_DIR
git pull origin main
print_success "Code updated"

# 3. Stop services
echo "Step 3: Stopping services..."
docker-compose down
print_success "Services stopped"

# 4. Rebuild containers
echo "Step 4: Rebuilding containers..."
docker-compose build --no-cache
print_success "Containers rebuilt"

# 5. Database migrations
echo "Step 5: Running database migrations..."
docker-compose run --rm api alembic upgrade head
print_success "Migrations applied"

# 6. Start services
echo "Step 6: Starting services..."
docker-compose up -d
print_success "Services started"

# 7. Health check
echo "Step 7: Running health checks..."
sleep 10

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API is healthy"
else
    print_error "API health check failed"
    exit 1
fi

# Check RabbitMQ
if curl -f -u guest:guest http://localhost:15672/api/overview > /dev/null 2>&1; then
    print_success "RabbitMQ is healthy"
else
    print_error "RabbitMQ health check failed"
    exit 1
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL health check failed"
    exit 1
fi

echo ""
echo "=== Deployment Complete ==="
echo "API: http://your-server-ip:8000"
echo "API Docs: http://your-server-ip:8000/docs"
echo "RabbitMQ Management: http://your-server-ip:15672"
```

Make it executable:
```bash
chmod +x deploy.sh
```

### Agent Installation Script (Windows)

Create `install_agent.bat`:

```batch
@echo off
echo ===================================
echo FTP Transfer Agent Installation
echo ===================================

REM Configuration
set CENTRAL_SERVER=http://your-central-server:8000
set INSTALL_DIR=C:\FTPTransferAgent
set SERVICE_NAME=FTPTransferAgent

echo.
echo Step 1: Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo [OK] Directory created: %INSTALL_DIR%

echo.
echo Step 2: Installing Python dependencies...
cd /d "%INSTALL_DIR%"
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Dependencies installed

echo.
echo Step 3: Configuring agent...
(
echo {
echo   "central_server_url": "%CENTRAL_SERVER%/api",
echo   "heartbeat_interval": 60,
echo   "task_check_interval": 30,
echo   "compression_enabled": true,
echo   "compression_type": "gzip"
echo }
) > "%INSTALL_DIR%\data\config.json"
echo [OK] Configuration created

echo.
echo Step 4: Building agent executable...
pyinstaller --onefile ^
    --name FTPTransferAgent ^
    --add-data "data;data" ^
    --hidden-import=paramiko ^
    --hidden-import=ftplib ^
    --hidden-import=lz4 ^
    agent\main.py
echo [OK] Executable built

echo.
echo Step 5: Installing as Windows Service...
python agent\service\windows_service.py install
python agent\service\windows_service.py start
echo [OK] Service installed and started

echo.
echo ===================================
echo Installation Complete!
echo ===================================
echo Service Name: %SERVICE_NAME%
echo Install Location: %INSTALL_DIR%
echo.
echo To manage the service:
echo   - Start:   net start %SERVICE_NAME%
echo   - Stop:    net stop %SERVICE_NAME%
echo   - Status:  sc query %SERVICE_NAME%
echo.
pause
```

### Systemd Service Files (Linux Deployment)

Create `/etc/systemd/system/ftp-api.service`:

```ini
[Unit]
Description=FTP Transfer API Service
After=network.target postgresql.service rabbitmq-server.service redis.service

[Service]
Type=simple
User=ftp-service
WorkingDirectory=/opt/ftp-transfer-system
Environment="PATH=/opt/ftp-transfer-system/venv/bin"
ExecStart=/opt/ftp-transfer-system/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/ftp-workers@.service`:

```ini
[Unit]
Description=FTP Transfer Worker - %i
After=network.target rabbitmq-server.service

[Service]
Type=simple
User=ftp-service
WorkingDirectory=/opt/ftp-transfer-system
Environment="PATH=/opt/ftp-transfer-system/venv/bin"
ExecStart=/opt/ftp-transfer-system/venv/bin/python -m app.workers.worker_launcher %i
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable ftp-api
sudo systemctl enable ftp-workers@task
sudo systemctl enable ftp-workers@agent
sudo systemctl enable ftp-workers@log
sudo systemctl enable ftp-workers@alert

# Start services
sudo systemctl start ftp-api
sudo systemctl start ftp-workers@task
sudo systemctl start ftp-workers@agent
sudo systemctl start ftp-workers@log
sudo systemctl start ftp-workers@alert

# Check status
sudo systemctl status ftp-api
```

---

## Testing Guide

### 1. Test Central Server

```bash
# Test API health
curl http://localhost:8000/health

# Test agent registration
curl -X POST http://localhost:8000/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "test-agent-01",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "os_info": "Windows 10",
    "agent_version": "1.0.0"
  }'

# Test task creation
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "agent_id": "YOUR_AGENT_ID",
    "task_type": "scheduled",
    "source_path": "C:\\data\\test.txt",
    "destination_path": "/uploads/test.txt",
    "protocol": "sftp",
    "compression_enabled": true
  }'

# List agents
curl http://localhost:8000/api/agents/

# View API documentation
# Open browser: http://localhost:8000/docs
```

### 2. Test Agent Locally

```bash
# Run agent in test mode
python agent/main.py

# Check logs
tail -f logs/agent.log

# Test file compression
python -c "
from agent.core.compressor import FileCompressor
result = FileCompressor.compress_file('test.txt', 'test.txt.gz', 'gzip')
print(f'Compressed: {result}')
"

# Test FTP connection
python -c "
from agent.core.transfer_engine import TransferEngine
engine = TransferEngine('sftp')
success = engine.connect('ftp.example.com', 22, 'user', 'pass')
print(f'Connected: {success}')
"
```

### 3. Test Message Queue

```bash
# Check RabbitMQ queues
curl -u guest:guest http://localhost:15672/api/queues

# Publish test message
python -c "
from app.messaging.producers import TaskProducer
import uuid
TaskProducer.publish_task_assignment(
    task_id=uuid.uuid4(),
    agent_id=uuid.uuid4(),
    task_data={'test': 'data'}
)
print('Message published')
"

# Check if message was consumed
docker-compose logs worker_task
```

### 4. End-to-End Test

```python
# test_e2e.py
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def test_full_workflow():
    print("Starting E2E test...")
    
    # 1. Register agent
    print("1. Registering agent...")
    response = requests.post(f"{BASE_URL}/agents/register", json={
        "hostname": "e2e-test-agent",
        "ip_address": "192.168.1.200",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "os_info": "Test OS",
        "agent_version": "1.0.0"
    })
    assert response.status_code == 201
    agent_id = response.json()['agent_id']
    print(f"   Agent registered: {agent_id}")
    
    # 2. Get access token
    print("2. Getting access token...")
    response = requests.post(f"{BASE_URL}/auth/token", params={"agent_id": agent_id})
    assert response.status_code == 200
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("   Token obtained")
    
    # 3. Create task
    print("3. Creating transfer task...")
    response = requests.post(f"{BASE_URL}/tasks/", headers=headers, json={
        "agent_id": agent_id,
        "task_type": "on_demand",
        "source_path": "/test/data.txt",
        "destination_path": "/uploads/data.txt",
        "protocol": "ftp",
        "compression_enabled": True
    })
    assert response.status_code == 201
    task_id = response.json()['task_id']
    print(f"   Task created: {task_id}")
    
    # 4. Agent fetches tasks
    print("4. Fetching pending tasks...")
    response = requests.get(f"{BASE_URL}/agents/{agent_id}/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0
    print(f"   Found {len(tasks)} pending task(s)")
    
    # 5. Submit transfer log
    print("5. Submitting transfer log...")
    response = requests.post(f"{BASE_URL}/logs/", headers=headers, json={
        "task_id": task_id,
        "agent_id": agent_id,
        "file_name": "data.txt",
        "file_size_bytes": 1024000,
        "compressed_size_bytes": 512000,
        "checksum_local": "abc123def456",
        "checksum_remote": "abc123def456",
        "transfer_start": "2025-10-21T10:00:00",
        "transfer_end": "2025-10-21T10:01:30",
        "duration_seconds": 90,
        "transfer_speed_mbps": 0.11,
        "status": "success",
        "error_message": None,
        "retry_attempt": 0
    })
    assert response.status_code == 201
    print("   Log submitted successfully")
    
    # 6. Verify task completion
    print("6. Verifying task status...")
    time.sleep(2)  # Wait for async processing
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    task_status = response.json()['status']
    print(f"   Task status: {task_status}")
    
    print("\n✓ E2E test completed successfully!")

if __name__ == "__main__":
    test_full_workflow()
```

Run test:
```bash
python test_e2e.py
```

---

## Monitoring and Maintenance

### View Logs

```bash
# Docker logs
docker-compose logs -f api
docker-compose logs -f worker_task
docker-compose logs -f celery_worker

# System logs (if using systemd)
sudo journalctl -u ftp-api -f
sudo journalctl -u ftp-workers@task -f
```

### Database Queries

```sql
-- Check agent status
SELECT agent_id, hostname, status, last_heartbeat 
FROM agents 
ORDER BY last_heartbeat DESC;

-- Check task statistics
SELECT status, COUNT(*) as count 
FROM tasks 
GROUP BY status;

-- Check recent transfer logs
SELECT * FROM transfer_logs 
ORDER BY created_at DESC 
LIMIT 10;

-- Check failed transfers
SELECT tl.*, t.source_path, a.hostname
FROM transfer_logs tl
JOIN tasks t ON tl.task_id = t.task_id
JOIN agents a ON tl.agent_id = a.agent_id
WHERE tl.status = 'failed'
ORDER BY tl.created_at DESC;
```

### Performance Monitoring

```bash
# Check RabbitMQ queue lengths
curl -u guest:guest http://localhost:15672/api/queues | jq '.[] | {name: .name, messages: .messages}'

# Check database connections
docker-compose exec postgres psql -U ftp_user -d ftp_central -c "SELECT count(*) FROM pg_stat_activity;"

# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Check system resources
docker stats
```

---

## Troubleshooting Common Issues

### Issue 1: Agent Can't Connect to Central Server

**Symptoms:** Agent logs show connection refused or timeout

**Solutions:**
```bash
# Check if API is running
curl http://central-server:8000/health

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Check network connectivity from agent PC
ping central-server-ip
telnet central-server-ip 8000
```

### Issue 2: RabbitMQ Messages Not Being Processed

**Symptoms:** Tasks stuck in "pending", queues building up

**Solutions:**
```bash
# Check if workers are running
docker-compose ps

# Check worker logs for errors
docker-compose logs worker_task

# Restart workers
docker-compose restart worker_task worker_agent worker_log worker_alert

# Check RabbitMQ connections
curl -u guest:guest http://localhost:15672/api/connections
```

### Issue 3: Database Connection Errors

**Symptoms:** "connection refused" or "too many connections"

**Solutions:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection limit
docker-compose exec postgres psql -U ftp_user -d ftp_central -c "SHOW max_connections;"

# View active connections
docker-compose exec postgres psql -U ftp_user -d ftp_central -c "SELECT count(*) FROM pg_stat_activity;"

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue 4: High Memory Usage

**Symptoms:** System becomes slow, OOM killer triggers

**Solutions:**
```bash
# Check memory usage
free -h
docker stats

# Limit container memory in docker-compose.yml
services:
  api:
    mem_limit: 512m
  worker_task:
    mem_limit: 256m

# Optimize Celery workers
celery -A app.workers.task_scheduler worker --max-memory-per-child=200000

# Enable swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Security Checklist

- [ ] Change default passwords (PostgreSQL, RabbitMQ)
- [ ] Use strong SECRET_KEY in production
- [ ] Enable SSL/TLS for API (use Nginx with Let's Encrypt)
- [ ] Use SFTP/FTPS instead of plain FTP
- [ ] Restrict database access to localhost
- [ ] Use firewall to limit port access
- [ ] Rotate JWT tokens regularly
- [ ] Encrypt FTP credentials in database
- [ ] Enable RabbitMQ SSL
- [ ] Regular security updates (apt update && apt upgrade)
- [ ] Monitor failed login attempts
- [ ] Set up log rotation
- [ ] Backup database regularly
- [ ] Use environment variables for secrets (never commit to git)

---

## Next Steps

1. **Set up central server** using Docker Compose
2. **Test API** using Swagger UI at http://localhost:8000/docs
3. **Deploy agent** on 1-2 test PCs
4. **Verify end-to-end** workflow with test transfers
5. **Build dashboard** for monitoring (React/Vue frontend)
6. **Gradually roll out** to remaining PCs
7. **Set up monitoring** (Prometheus + Grafana)
8. **Configure alerting** (email, Slack, SMS)
9. **Document procedures** for your team
10. **Train users** on dashboard and troubleshooting

---

## Support and Resources

### Official Documentation
- FastAPI: https://fastapi.tiangolo.com/
- PostgreSQL: https://www.postgresql.org/docs/
- RabbitMQ: https://www.rabbitmq.com/documentation.html
- Celery: https://docs.celeryproject.org/
- Docker: https://docs.docker.com/
- SQLAlchemy: https://docs.sqlalchemy.org/

### Community
- FastAPI Discord: https://discord.gg/VQjSZaeJmf
- Stack Overflow tags: fastapi, rabbitmq, celery, postgresql

### Learning Resources
- Docker Tutorial: https://docker-curriculum.com/
- RabbitMQ Tutorial: https://www.rabbitmq.com/getstarted.html
- Celery Tutorial: https://docs.celeryproject.org/en/stable/getting-started/

---

Good luck with your project! 🚀
