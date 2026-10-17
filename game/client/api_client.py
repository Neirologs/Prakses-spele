"""All of the communication with the server in one place. The game her calls only the register, login un submit_score."""
import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5   

session = requests.Session()
session.trust_env = False   


class ApiError(Exception):
    """Error, that can be shown to the player. status is an HTTP number (or None, if the server is not reachable)."""
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def _post(path, data, headers=None, messages=None):
    messages = messages or {}
    try:
        response = session.post(BASE_URL + path, json=data, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        raise ApiError("Cannot reach the server. Is it running?")
    if response.status_code >= 400:
        if response.status_code == 422:
            text = "Invalid input (name 2-25 characters, password 3+)"
        else:
            text = messages.get(response.status_code, "Server error " + str(response.status_code))
        raise ApiError(text, response.status_code)
    return response.json()


def register(name, password):
    _post("/register", {"name": name, "password": password},
          messages={400: "Name already taken"})


def login(name, password):
    """Returns a token."""
    data = _post("/login", {"name": name, "password": password},
                 messages={401: "Wrong name or password"})
    return data["token"]


def submit_score(token, centiseconds):
    """centiseconds"""
    _post("/scores", {"score": centiseconds}, headers={"token": token},
          messages={401: "Not logged in"})