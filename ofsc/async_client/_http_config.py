"""Library-neutral HTTP transport configuration for AsyncOFSC.

The fields exposed here are deliberately scalar (``int``, ``float``, ``bool``,
``str``) so the public surface does not leak the underlying HTTP library's
types. ``AsyncOFSC.__aenter__`` translates this config into whatever the
current transport library understands.
"""

from pydantic import BaseModel, ConfigDict, Field


class HTTPClientConfig(BaseModel):
    """Optional transport tuning for ``AsyncOFSC``.

    All fields are optional; defaults preserve ``AsyncOFSC``'s historical
    behavior (HTTP/2 on, transport-library default pool and timeout, no
    retries, no proxy, system trust store).
    """

    model_config = ConfigDict(frozen=True)

    max_concurrency: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Maximum number of concurrent connections to the OFSC tenant. "
            "Requests submitted beyond this cap (e.g. via asyncio.gather) "
            "queue waiting for a slot. None keeps the transport library's "
            "default pool size."
        ),
    )
    timeout: float | None = Field(
        default=None,
        gt=0,
        description=("Total per-request timeout in seconds. None keeps the transport library's default (httpx defaults to 5s)."),
    )
    max_retries: int = Field(
        default=0,
        ge=0,
        description=("Number of transport-level retries on connection errors. Does not retry HTTP 4xx/5xx responses."),
    )
    proxy: str | None = Field(
        default=None,
        description="Proxy URL (e.g. 'http://proxy.example.com:8080').",
    )
    verify_ssl: bool = Field(
        default=True,
        description="Whether to verify TLS certificates.",
    )
    http2: bool = Field(
        default=True,
        description="Whether to enable HTTP/2.",
    )
    follow_redirects: bool = Field(
        default=False,
        description="Whether to follow HTTP redirects automatically.",
    )
    trust_env: bool = Field(
        default=True,
        description=("Whether to honor environment variables for proxy, SSL CA bundle, and netrc configuration."),
    )
