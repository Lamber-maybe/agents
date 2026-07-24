---
title: Notes on FastAPI authentication
date: 2026-07-18
---

In the modern world of web development, security is more important than ever. Authentication is one of those things every project needs. I recently set up auth for a side project and took some notes along the way, so I figured I'd write them up in case they're useful to someone.

FastAPI doesn't ship with a full auth system the way Django does. It gives you the building blocks: dependency injection, the OAuth2PasswordBearer helper, and good docs integration. You have to assemble the rest yourself, which is both a blessing and a curse. The blessing is you understand every piece. The curse is there are a lot of ways to get it subtly wrong.

The basic flow I ended up with is the standard one. The user posts credentials to a login endpoint. The server verifies the password against a stored hash, then returns a short-lived access token (a JWT) and a longer-lived refresh token. The client sends the access token in the Authorization header on every request. When it expires, the client calls a refresh endpoint with the refresh token to get a new pair.

For password hashing I used bcrypt via passlib. Don't use sha256 or md5 for passwords, they are designed to be fast which is exactly what you don't want. bcrypt has a work factor which makes brute forcing expensive. Argon2 is also a fine choice and arguably better, but bcrypt has been battle tested for decades and passlib makes either one a one-liner.

For the tokens I used python-jose at first and then switched to pyjwt because it's smaller and maintained more actively. The access token contains the user id in the sub claim and an exp claim set to 15 minutes out. The refresh token lives for 7 days and is stored hashed in the database, so it can be revoked. That last part matters: pure stateless JWTs cannot be revoked before expiry, which is a problem if a token leaks. Storing refresh tokens server side gives you a kill switch while keeping access token verification stateless and fast.

Here is the core of the token creation code:

```python
from datetime import datetime, timedelta, timezone
import jwt

SECRET_KEY = settings.secret_key  # from env, never hardcoded
ALGORITHM = "HS256"

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

And the dependency that protects routes:

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    return get_user_or_401(int(payload["sub"]))
```

A few mistakes I made that might save you time. I initially put the token expiry at 24 hours because refreshing seemed like a hassle, which defeats the point of short-lived tokens. I also forgot to set the type claim at first, which meant a refresh token could be used as an access token. And I spent an evening debugging 401s that turned out to be the tokenUrl in OAuth2PasswordBearer not matching my actual login route, which only breaks the interactive docs, not the API itself, so everything worked in curl and failed in the browser.

Where to store tokens on the client is its own can of worms. localStorage is vulnerable to XSS, httpOnly cookies are vulnerable to CSRF unless you add SameSite and a CSRF token. For my case, an SPA talking to an API on the same domain, I went with httpOnly SameSite=Lax cookies for the refresh token and kept the access token in memory. There are good arguments for other setups depending on your threat model.

That's about it. The full example repo is linked at the end. Auth is one of those topics where the details matter a lot, so test the failure paths, not just the happy path.
