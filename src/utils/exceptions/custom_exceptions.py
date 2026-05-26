

# src/utils/exceptions/custom_exceptions.py

from utils.exceptions.error_codes import ErrorCodes


class BrewBaseException(Exception):

    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code  = error_code
        self.message     = message
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "status"     : "error",
            "error_code" : self.error_code,
            "message"    : self.message
        }


