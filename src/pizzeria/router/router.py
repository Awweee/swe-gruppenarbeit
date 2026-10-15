from typing import Final
from fastapi import APIRouter

from pizzeria.service.service import Service
from pizzeria.repository.repository import Repository
from pizzeria.security.user import User

pizzeria_router: Final = APIRouter(tags=["Pizzerias"])
@pizzeria_router.get("/pizzerias/{pizzeria_id}", response_model=Service)
def get_by_id(pizzeria_id: int):
    """Pizzeria anhand der ID suchen."""
    service: Final = Service(repo=Repository())
    user: Final = User(username="testuser", roles=["USER"])
    return service.find_by_id(pizzeria_id=pizzeria_id, user=user)
