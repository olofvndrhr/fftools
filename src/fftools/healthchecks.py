import socket

from loguru import logger as log
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from fftools.web import req


class HealthChecks:
    """ping healthchecks.

    you can use <HOSTNAME> in the path for the formatted hostname of the device.
    """

    def __init__(
        self, url: str, path: str, ping_key: str | None = None, user_agent: str | None = None
    ) -> None:
        """Init the healthchecks api.

        Args:
            url: base url of the healthchecks instance.
            path: ping path. full path if `ping_key` is not used,
                else only the part after the `ping_key`.
            ping_key: ping key to use.
            user_agent: custom user-agent to set for requests.
        """
        self.hc_hostname = socket.gethostname().replace(".", "")
        self.host = url
        self.path = path.replace("<HOSTNAME>", self.hc_hostname)
        self.ping_key = ping_key
        self.user_agent = user_agent

        self.url = self._get_url()
        self.headers = {"User-Agent": self.user_agent} if self.user_agent else None

        log.debug(f"init healthchecks={self.url}, user-agent={self.user_agent}")

    def _get_url(self) -> str:
        path = f"ping/{self.path}"
        if self.path and self.ping_key:
            path = f"ping/{self.ping_key}/{self.path}"

        # remove double '/' and the trailing '/'
        path = path.replace("//", "/")
        path = path.removesuffix("/")

        return f"{self.host}/{path}"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3), reraise=True)
    def _ping(self, path: str, message: str | None) -> tuple[int, str]:
        ping_url = self.url + path

        try:
            result = req("POST", ping_url, payload=message, headers=self.headers)
            result.raise_for_status()
        except Exception as exc:
            log.error(f"can't ping health-checks. exc={exc}")
            raise

        return result.status_code, result.text

    def success(self, message: str | None = None) -> tuple[int, str]:
        """Ping with status: success.

        used to end the job or signal success.

        Args:
            message: message to add to ping body.

        Returns:
            A tuple with (http response code, http response body).
        """
        log.info("health-checks: success...")
        status_path = ""
        status_code, status_text = self._ping(status_path, message)

        return status_code, status_text

    def start(self, message: str | None = None) -> tuple[int, str]:
        """Ping with status: start.

        starts the timer of the healthchecks job.

        Args:
            message: message to add to ping body.

        Returns:
            A tuple with (http response code, http response body).
        """
        log.info("health-checks: start...")
        status_path = "/start"
        status_code, status_text = self._ping(status_path, message)

        return status_code, status_text

    def fail(self, message: str | None = None) -> tuple[int, str]:
        """Ping with status: fail.

        fails the current job.

        Args:
            message: message to add to ping body.

        Returns:
            A tuple with (http response code, http response body).
        """
        log.info("health-checks: fail...")
        status_path = "/fail"
        status_code, status_text = self._ping(status_path, message)

        return status_code, status_text

    def exit_code(self, exit_code: str | int, message: str | None = None) -> tuple[int, str]:
        """Ping with status: exit_code.

        send the exit code of the program to healthchecks.

        Args:
            exit_code: exit code to report.
            message: message to add to ping body.

        Returns:
            A tuple with (http response code, http response body).
        """
        log.info(f"health-checks: exit code={exit_code}...")
        status_path = f"/{exit_code}"
        status_code, status_text = self._ping(status_path, message)

        return status_code, status_text

    def log(self, message: str) -> tuple[int, str]:
        """Ping with status: log.

        sends a log to the current job. does not stop or fail the job.

        Args:
            message: message to add to ping body.

        Returns:
            A tuple with (http response code, http response body).
        """
        log.info("health-checks: log...")
        status_path = "/log"
        status_code, status_text = self._ping(status_path, message)

        return status_code, status_text
