from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncio
import aio_pika
import json
import logging
from contextlib import asynccontextmanager

from core.database import Base, engine, SessionLocal
from core.config import settings
from api.endpoints import notifications
from services.notification_service import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification")

Base.metadata.create_all(bind=engine)

async def consume_messages():
    while True:
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            async with connection:
                channel = await connection.channel()
                queue = await channel.declare_queue("log.critical.alerts", durable=True)
                
                logger.info("Connected to RabbitMQ, waiting for critical logs...")
                async for message in queue:
                    async with message.process():
                        payload = json.loads(message.body.decode())
                        db = SessionLocal()
                        try:
                            svc = NotificationService(db)
                            svc.process_alert(payload)
                        finally:
                            db.close()
        except Exception as e:
            logger.error(f"RabbitMQ connection failed, retrying in 5s: {str(e)}")
            await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(consume_messages())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(title="Notification Service", lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"status": "error", "error": exc.errors()})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"status": "error", "error": str(exc.detail)})

app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
