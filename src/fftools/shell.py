import bz2
import gzip
import lzma
import shutil
import subprocess
from pathlib import Path
from typing import Literal

from fabric import Connection
from loguru import logger as log

from fftools.other import pop_dict


def run_command(
    command: str | list[str] | tuple[str] | set[str],
    timeout: int = 10,
    check_ecode: bool = True,
    **kwargs,
) -> tuple[int, str, str]:
    """Run local shell command.

    Args:
        command: command to run.
        timeout: timeout in seconds.
        check_ecode: if exception should be raised on non-zero exit codes.
        kwargs: other kwargs directly supplied to `subprocess.run`

    Raises:
        TypeError: if command is not either a `str`, `list`, `tuple` or `set`.
        exc: if `check_ecode` is `True` and the exit code is not 0.

    Returns:
        A tuple of (exit code, stdout, stderr).
    """
    if isinstance(command, str):
        cmd = command.split()
    elif isinstance(command, list | tuple | set):
        cmd = list(command)
    else:
        raise TypeError

    # remove args from kwargs
    filtered_kwargs = pop_dict(
        kwargs,
        [
            "check",
            "timeout",
            "capture_output",
            "encoding",
        ],
    )

    log.info(f"running command='{' '.join(cmd)}'. {timeout=}")
    try:
        proc = subprocess.run(
            cmd,
            check=check_ecode,
            timeout=timeout,
            capture_output=True,
            encoding="utf8",
            **filtered_kwargs,
        )
    except Exception as exc:
        log.error(f"can't run {command=}. {exc=}")
        raise

    stdout: str = proc.stdout.strip()
    stderr: str = proc.stderr.strip()
    exit_code: int = proc.returncode

    return exit_code, stdout, stderr


def run_ssh_command(
    command: str | list[str] | tuple[str] | set[str],
    hostname: str,
    username: str = "root",
    port: int = 22,
    timeout: int = 10,
    check_ecode: bool = True,
    password: str | None = None,
    **kwargs,
) -> tuple[int, str, str]:
    """Run command on remote machine via ssh.

    Args:
        command: command to run.
        hostname: hostname of remote device.
        username: ssh username.
        port: ssh port.
        timeout: command timeout.
        check_ecode: if exception should be raised on non-zero exit codes.
        password: ssh user password if not authenticated via ssh keys.
        kwargs: other kwargs directly supplied to `fabric.Connection.run`

    Raises:
        TypeError: if command is not either a `str`, `list`, `tuple` or `set`.
        exc: if `check_ecode` is `True` and the exit code is not 0.

    Returns:
        A tuple of (exit code, stdout, stderr).
    """
    if isinstance(command, str):
        cmd = command
    elif isinstance(command, list | tuple | set):
        cmd = " ".join(command)
    else:
        raise TypeError

    # remove args from kwargs
    filtered_kwargs = pop_dict(
        kwargs,
        [
            "hide",
            "warn",
            "timeout",
        ],
    )

    log.info(
        f"running ssh command on host={username}@{hostname}:{port}, command='{cmd}'. {timeout=}",
    )
    try:
        connection = Connection(
            host=hostname,
            user=username,
            port=port,
            connect_timeout=10,
            connect_kwargs={"password": password} if password else {},
        )
        with connection as con:
            proc = con.run(
                cmd,
                hide=True,
                warn=(not check_ecode),
                timeout=timeout,
                encoding="utf8",
                **filtered_kwargs,
            )
    except Exception as exc:
        log.error(f"can't run ssh {command=}. {exc=}")
        raise

    stdout: str = proc.stdout.strip()
    stderr: str = proc.stderr.strip()
    exit_code: int = proc.return_code

    return exit_code, stdout, stderr


def extract_archive(archive: Path) -> None:
    """Extract an archive file.

    supportet are: tar, zip, gzip, bzip2 and xz.

    Args:
        archive: path of the archive to extract.
    """
    log.debug(f"trying to extract archive={archive}")

    dual_suffix = "".join(archive.suffixes[-2:])
    archive_suffix = dual_suffix if ".tar." in dual_suffix else archive.suffix

    tarzip_suffixes = [".tar.bz2", ".tbz2", ".tar.gz", ".tgz", ".tar", ".tar.xz", ".txz", ".zip"]
    xz_suffixes = [".xz"]
    bz_suffixes = [".bz", ".bzip", ".bz2", ".bzip2"]
    gz_suffixes = [".gz", ".gzip"]

    if archive_suffix in tarzip_suffixes:
        extract_dir = archive.parent / archive.name.removesuffix(archive_suffix)
        log.info(f"extracting tarzip archive={archive}, extract to={extract_dir}")
        shutil.unpack_archive(archive, extract_dir)
    elif archive_suffix in bz_suffixes:
        extract_file("bzip", archive, archive.with_suffix(""))
    elif archive_suffix in gz_suffixes:
        extract_file("gzip", archive, archive.with_suffix(""))
    elif archive_suffix in xz_suffixes:
        extract_file("xz", archive, archive.with_suffix(""))
    else:
        log.debug("no matching archive suffix found")


def extract_file(atype: Literal["gzip", "bzip", "xz"], infile: Path, outfile: Path) -> None:
    """Extract file.

    Args:
        atype: archive type.
        infile: compressed input file
        outfile: decompressed output file.

    Raises:
        ValueError: on invalid `atype`.
    """
    log.info(f"extracting {atype} file={infile} -> {outfile}")
    try:
        match atype:
            case "gzip":
                with gzip.open(infile, "rb") as i, outfile.open("wb") as o:
                    shutil.copyfileobj(i, o, length=64 * 1024)
            case "bzip":
                with bz2.open(infile, "rb") as i, outfile.open("wb") as o:
                    shutil.copyfileobj(i, o, length=64 * 1024)
            case "xz":
                with lzma.open(infile, "rb") as i, outfile.open("wb") as o:
                    shutil.copyfileobj(i, o, length=64 * 1024)
            case _:
                log.error(f"invalid archive type={atype}")
                raise ValueError
    except Exception as exc:
        log.error(f"cant extract {atype} archive={infile}. {exc=}")
