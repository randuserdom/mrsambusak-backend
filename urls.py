from fastapi import APIRouter
from views import (
    register_user,
    login,
    get_messages,
    delete_message,
    get_all_users,
    get_user,
)

router = APIRouter()

router.add_api_route("/register", register_user, methods=["POST"])
router.add_api_route("/login", login, methods=["POST"])
router.add_api_route("/messages", get_messages, methods=["GET"])
router.add_api_route("/message", delete_message, methods=["GET", "DELETE"])
router.add_api_route("/get_all_users", get_all_users, methods=["GET"])
router.add_api_route("/user/{user_id}", get_user, methods=["GET"])
