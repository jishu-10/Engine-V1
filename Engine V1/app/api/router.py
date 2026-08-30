from fastapi import APIRouter

from app.api.routes import health, profile, prompts, responses, similarity, users, validation

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(prompts.router)
api_router.include_router(responses.router)
api_router.include_router(profile.router)
api_router.include_router(similarity.router)
api_router.include_router(validation.router)

