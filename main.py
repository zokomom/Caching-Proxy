#!/usr/bin/env python3
import argparse
from fastapi import FastAPI, Request
from fastapi.responses import Response
import uvicorn
import httpx
import json
import os

app = FastAPI()

CACHE_FILE = "cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Cache file corrupted, starting fresh!")
            return {}
    return {}


def save_cache(cache):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving cache: {e}")


cache = load_cache()


@app.get("/{path:path}")
async def proxy_(path: str, request: Request):
    if path in cache:
        content = cache[path]["content"].encode("utf-8")  # ✅ string → bytes
        status_code = cache[path]["status_code"]
        headers = cache[path]["headers"]
        headers["X-Cache"] = "HIT"
        return Response(status_code=status_code, content=content, headers=headers)
    else:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{app.state.origin}/{path}", follow_redirects=True)
            try:
                cache[path] = {
                    "content": res.content.decode("utf-8"),
                    "status_code": res.status_code,
                    "headers": dict(res.headers)
                }
                save_cache(cache)
            except UnicodeDecodeError:
                pass  # skip caching binary files like images, icons
            headers = dict(res.headers)
            headers['X-Cache'] = 'MISS'
            return Response(content=res.content, status_code=res.status_code, headers=headers)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--port", type=int)
    parser.add_argument("--origin", type=str)
    parser.add_argument("--clear-cache", action="store_true")
    args = parser.parse_args()

    PORT = args.port
    CLEAR_CACHE_FLAG = args.clear_cache  # True or False
    if CLEAR_CACHE_FLAG:
        cache.clear()
        save_cache(cache)
        print("Cleared Cache!")
        exit()
    app.state.origin = args.origin
    uvicorn.run(app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
