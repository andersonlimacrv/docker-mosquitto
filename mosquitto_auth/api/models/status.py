from enum import Enum

class UserStatus(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    NOT_FOUND = "NOT FOUND"
    ERROR = "ERROR"

class CertificateStatus(str, Enum):
    CREATED = "CREATED"
    ERROR = "ERROR"