from pathlib import Path
from typing import Any, Literal

import dns.resolver
import httpx
from loguru import logger as log

from fftools.other import pop_dict


def download_file(
    url: str,
    download_path: Path,
    timeout: int = 30,
    follow_redirects: bool = True,
    chunk_size: int | None = 64 * 1024,
    username: str | None = None,
    password: str | None = None,
    **kwargs,
) -> None:
    """Download a file with httpx.stream.

    Args:
        url: url of the file.
        download_path: ath to save the file to.
        timeout: timeout of the request in seconds.
        follow_redirects: follow HTTP 3XX redirects. `None` sets it to the server response default.
        chunk_size: size of the chunks which are downloaded.
        username: username for basic auth. if unset no authentication is used.
        password: password for basic auth. if unset no authentication is used.
        kwargs: other kwargs directly supplied to `httpx.request`

    Raises:
        ValueError: if requested file size is 0 bytes.
        exc: on download errors.
    """
    # remove args from kwargs
    filtered_kwargs = pop_dict(
        kwargs,
        [
            "url",
            "timeout",
            "follow_redirects",
            "auth",
        ],
    )
    auth = httpx.BasicAuth(username=username, password=password) if username and password else None

    log.info(f"HTTP DOWNLOAD {url}")
    try:
        with (
            httpx.stream(
                "GET",
                url,
                timeout=timeout,
                follow_redirects=follow_redirects,
                auth=auth,
                **filtered_kwargs,
            ) as r,
            download_path.open(mode="wb") as f,
        ):
            r.raise_for_status()
            content_length = int(r.headers.get("content-length", 0))
            if content_length <= 0:
                log.error(f"invalid content length={content_length}")
                raise ValueError

            for chunk in r.iter_bytes(chunk_size=chunk_size):
                f.write(chunk)
    except Exception as exc:
        log.error(f"can't save file={download_path}. {exc=}")
        download_path.unlink(missing_ok=True)
        raise


def upload_file(
    method: Literal["POST", "PUT", "PATCH"],
    url: str,
    file_path: Path,
    timeout: int = 30,
    username: str | None = None,
    password: str | None = None,
    **kwargs,
) -> httpx.Response:
    """Upload a file with httpx.

    Args:
        method: http method to use for the upload.
        url: upload url.
        file_path: path of file to upload.
        timeout: timeout of the request in seconds.
        username: username for basic auth. if unset no authentication is used.
        password: password for basic auth. if unset no authentication is used.
        kwargs: other kwargs directly supplied to `httpx.request`

    Raises:
        exc: on upload errors.

    Returns:
        A `httpx.Response` object.
    """
    # remove args from kwargs
    filtered_kwargs = pop_dict(
        kwargs,
        [
            "url",
            "timeout",
            "auth",
        ],
    )
    auth = httpx.BasicAuth(username=username, password=password) if username and password else None

    log.info(f"HTTP UPLOAD {method} {url}")
    try:
        files = {"upload-file": file_path.open("rb")}
        response = httpx.request(
            method=method,
            url=url,
            timeout=timeout,
            files=files,
            auth=auth,
            **filtered_kwargs,
        )
    except Exception as exc:
        log.error(f"cant upload file={file_path} {exc=}")
        raise

    return response


def req(
    method: Literal["GET", "POST", "HEAD", "PUT", "DELETE", "PATCH", "OPTIONS"],
    url: str,
    timeout: float = 5,
    default_headers: bool = True,
    follow_redirects: bool = True,
    payload: dict[str, Any] | str | bytes | None = None,
    username: str | None = None,
    password: str | None = None,
    **kwargs,
) -> httpx.Response:
    """Make a http(s) request.

    Args:
        method: HTTP method, e.g. GET.
        url: url for the request.
        timeout: timeout of the request in seconds.
        default_headers: send default headers for `content-type` and `accept`.
        follow_redirects: follow HTTP 3XX redirects.
        payload: data to send. either `dict`, `str` or `bytes`.
        username: username for basic auth. if unset no authentication is used.
        password: password for basic auth. if unset no authentication is used.
        kwargs: other kwargs directly supplied to `httpx.request`

    Raises:
        exc: on request errors.

    Returns:
        A `httpx.Response` object
    """
    _default_headers = {
        "accept": "application/json",
        "content-type": "application/json; charset=UTF-8",
    }
    headers = kwargs.get("headers", {}) or {}
    if isinstance(headers, dict) and default_headers:
        headers.update(_default_headers)
    if not isinstance(headers, dict):
        log.warning("headers are invalid. using only default ones.")
        headers = _default_headers

    # remove args from kwargs
    filtered_kwargs = pop_dict(
        kwargs,
        [
            "url",
            "timeout",
            "headers",
            "follow_redirects",
            "json",
            "content",
            "auth",
        ],
    )

    auth = httpx.BasicAuth(username=username, password=password) if username and password else None

    log.info(f"HTTP {method} {url}")
    try:
        response = httpx.request(
            method=method,
            url=url,
            timeout=timeout,
            headers=headers,
            follow_redirects=follow_redirects,
            json=payload if isinstance(payload, dict) else None,
            content=payload if isinstance(payload, str | bytes) else None,
            auth=auth,
            **filtered_kwargs,
        )
    except Exception as exc:
        log.error(f"error in {method} request. {exc=}")
        raise

    return response


def dig(fqdn: str, record_type: str) -> list[str]:
    """Resolve dns record.

    Args:
        fqdn: fqdn of record to resolve.
        record_type: type of record, e.g. A or AAA.

    Raises:
        ValueError: if no answer was found.
        exc: on resolving errors.

    Returns:
        A a list of resolved addresses.
    """
    record_type = record_type.upper()

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["9.9.9.9", "1.1.1.1"]
    resolver.timeout = 5
    resolver.lifetime = 5

    log.info(f"DIG {fqdn}")

    try:
        answer = resolver.resolve(fqdn, record_type)
        if not answer.rrset:
            raise ValueError
        resolved_records = [n.to_text() for n in answer.rrset]
    except Exception as exc:
        log.warning(f"error while resolving record(s). {exc=}")
        raise

    log.info(f"resolved record(s) {fqdn=}, {resolved_records=}")
    return resolved_records
