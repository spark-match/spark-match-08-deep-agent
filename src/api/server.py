"""Server entry point — run with `uv run python -m src`."""

import uvicorn

from src.api.app import create_app
from src.config import get_settings


def main() -> None:
    """Start the FastAPI server."""
    settings = get_settings()

    app = create_app()

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
