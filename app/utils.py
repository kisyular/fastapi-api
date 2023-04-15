# Import CryptContext
from passlib.context import CryptContext
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash the password
def hash_password(password):
    return pwd_context.hash(password)


# Verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
