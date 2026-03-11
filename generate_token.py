import jwt
import time
import os
from dotenv import load_dotenv

load_dotenv()

def generate_token(role="rtc"):
    api_key = os.getenv("VIDEOSDK_API_KEY")
    secret_key = os.getenv("VIDEOSDK_SECRET_KEY")

    if not api_key or not secret_key:
        print("Error: VIDEOSDK_API_KEY and VIDEOSDK_SECRET_KEY must be set in .env")
        return

    payload = {
        "apikey": api_key,
        "permissions": ["allow_join", "allow_mod"],
        "version": 2,
        "roles": [role],
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400,  # 24 hours
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

if __name__ == "__main__":
    import sys
    role = sys.argv[1] if len(sys.argv) > 1 else "rtc"
    token = generate_token(role=role)
    print(f"\nRole: {role}")
    print("-" * 40)
    print(token)
    print("-" * 40)
    if role == "rtc":
        print(f"\nUpdate .env: VIDEOSDK_AUTH_TOKEN={token}")
    else:
        print(f"\nUse this token in Authorization header for V2 API calls")
