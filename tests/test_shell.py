import shutil
import time
from pathlib import Path

import pytest
from loguru import logger as log

from fftools.shell import extract_archive, extract_file, run_command
from fftools.web import download_file


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


def test_extract_archive() -> None:
    url = "https://github.com/restic/restic/releases/download/v0.16.2/restic_0.16.2_linux_amd64.bz2"
    dl_path = TMPDIR / "restic_0.16.2_linux_amd64.bz2"
    download_file(url, dl_path)

    assert dl_path.exists()
    assert dl_path.is_file()

    extract_archive(dl_path)

    assert dl_path.with_suffix("").exists()
    assert dl_path.with_suffix("").is_file()

    # cleanup
    dl_path.unlink(missing_ok=True)
    dl_path.with_suffix("").unlink(missing_ok=True)


def test_extract_file() -> None:
    url = "https://github.com/restic/restic/releases/download/v0.16.2/restic_0.16.2_linux_amd64.bz2"
    dl_path = TMPDIR / "restic_0.16.2_linux_amd64.bz2"
    download_file(url, dl_path)

    assert dl_path.exists()
    assert dl_path.is_file()

    extract_file("bzip", dl_path, dl_path.with_suffix(".test"))

    assert dl_path.with_suffix(".test").exists()
    assert dl_path.with_suffix(".test").is_file()

    # cleanup
    dl_path.unlink(missing_ok=True)
    dl_path.with_suffix(".test").unlink(missing_ok=True)


def test_run_command_str() -> None:
    command = "echo hello"
    _ecode, stdout, stderr = run_command(command)

    assert stdout == "hello"
    assert stderr == ""


def test_run_command_invalid_arg() -> None:
    command = "echo hello"
    _ecode, stdout, stderr = run_command(command, check=False, capture_output=False)

    assert stdout == "hello"
    assert stderr == ""


def test_run_command_list() -> None:
    command = ["echo", "hello"]
    _ecode, stdout, stderr = run_command(command)

    assert stdout == "hello"
    assert stderr == ""


def test_run_command_tuple() -> None:
    command = ("echo", "hello")
    _ecode, stdout, stderr = run_command(command)

    assert stdout == "hello"
    assert stderr == ""
