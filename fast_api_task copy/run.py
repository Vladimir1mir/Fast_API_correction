import os

import uvicorn


def main() -> None:
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))

    uvicorn.run("app.app:app", host=host, port=port)


if __name__ == "__main__":
    main()
