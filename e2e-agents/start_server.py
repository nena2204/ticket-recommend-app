"""Start Django for Playwright: fresh database, demo data, then runserver.

Called by playwright.config.ts (webServer). Cross-platform, so it works the same in the
PyCharm terminal on Windows and in GitHub Actions on Linux.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = os.environ.get("E2E_PORT", "8001")
SETTINGS = "--settings=TicketRecommend.settings_e2e"


def manage(*args):
    subprocess.run([sys.executable, "manage.py", *args, SETTINGS], cwd=ROOT, check=True)


if __name__ == "__main__":
    (ROOT / "e2e_db.sqlite3").unlink(missing_ok=True)
    manage("migrate", "--noinput", "-v", "0")
    manage("seed_demo")
    # Blocking call (not os.execv) so Playwright can stop the whole process tree on Windows too.
    sys.exit(subprocess.call([sys.executable, "manage.py", "runserver",
                              f"127.0.0.1:{PORT}", "--noreload", SETTINGS], cwd=ROOT))
