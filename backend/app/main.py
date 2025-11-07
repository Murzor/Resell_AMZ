from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.routes import auth, settings as settings_route, search, product, calc, lists, alerts

# Configuration des logs
setup_logging(settings.LOG_LEVEL)

# Configuration Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )

app = FastAPI(
    title="API Arbitrage Amazon",
    description="API mono-utilisateur pour outil d'arbitrage Amazon",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(settings_route.router)
app.include_router(search.router)
app.include_router(product.router)
app.include_router(calc.router)
app.include_router(lists.router)
app.include_router(alerts.router)


@app.get("/")
def root():
    return {"message": "API Arbitrage Amazon", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}

