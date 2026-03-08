import argparse
from fastapi import FastAPI

app = FastAPI()

cache = {}
origin = ""


@app.get("/")
async def proxy():
    return "Hello World"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--port", type=int)
    parser.add_argument("--origin", type=str)
    parser.add_argument("--clear-cache", action="store_true")
    args = parser.parse_args()

    PORT = args.port
    ORIGIN = args.origin
    CLEAR_CACHE_FLAG = args.clear_cache  # True or False
