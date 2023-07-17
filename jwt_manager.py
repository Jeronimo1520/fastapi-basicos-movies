from jwt import encode, decode

def create_token(data: dict) -> str:
    token: str = encode(payload=data, key="ik5eaf2gpJo98snpZXfxI6dxSGf9QeHD",algorithm="HS256")
    return token

def validate_token(token:str) -> dict:
    data: dict = decode(token, key="ik5eaf2gpJo98snpZXfxI6dxSGf9QeHD",algorithms=['HS256'])
    return data

