import shutil
import time
from pathlib import Path

import pytest
from loguru import logger as log

from fftools.web import dig, download_file, req


TMPDIR = Path("tmp")


@pytest.fixture(autouse=True, scope="module")
def prepare_folders():  # noqa: ANN201
    TMPDIR.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(TMPDIR)


@pytest.fixture
def _wait_10s() -> None:
    log.info("sleeping 10 seconds because of timeouts")
    time.sleep(10)


@pytest.fixture
def _wait_20s() -> None:
    log.info("sleeping 20 seconds because of timeouts")
    time.sleep(20)


def test_req_get() -> None:
    url = "https://ifconfig.co"
    resp = req("GET", url)

    assert resp.status_code == 200


def test_req_get_invalid_arg() -> None:
    url = "https://ifconfig.co"
    resp = req("GET", url, headers={"test": "test"}, follow_redirects=False, content="test")

    assert resp.status_code == 200


def test_download() -> None:
    url = "https://debian.ethz.ch/debian/extrafiles"
    dl_path = TMPDIR / "testfile"
    download_file(url, dl_path)

    assert dl_path.exists()
    assert dl_path.is_file()
    assert dl_path.stat().st_size > 100000

    # cleanup
    dl_path.unlink(missing_ok=True)


def test_dig() -> None:
    fqdn = "nic.ch"
    rtype = "A"
    resp = dig(fqdn, rtype)

    assert resp == ["130.59.31.80"]
