"""Simulate a UI refactor so the Playwright healer agent has something to fix.

    python healer_demo.py break     # rename buttons like a developer would during a redesign
    python healer_demo.py restore   # put the original templates back

Workflow for the demo:
  1. generated tests pass            ->  npx playwright test
  2. python healer_demo.py break     ->  npx playwright test   (tests now fail)
  3. ask the healer agent to fix the failing tests (see prompts/03-healer.md)
  4. npx playwright test             (tests pass again, the healer updated the locators)
  5. python healer_demo.py restore   (and let the healer run once more, or git checkout the tests)
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP = Path(__file__).resolve().parent / ".healer-demo-backup"

# template -> list of (original text, text after the "redesign")
CHANGES = {
    "templates/events/event_detail.html": [
        ('data-tt="{{ tt.id }}">Buy tickets</button>', 'data-tt="{{ tt.id }}">Add to cart</button>'),
        ('class="btn btn-primary">Додади</button>', 'class="btn btn-primary">Потврди</button>'),
    ],
    "templates/events/contact.html": [
        ('<button type="submit">Send</button>', '<button type="submit">Send message</button>'),
    ],
}


def break_ui():
    if BACKUP.exists():
        sys.exit("Already broken. Run 'python healer_demo.py restore' first.")
    for relative, replacements in CHANGES.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        (BACKUP / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, BACKUP / relative)
        for old, new in replacements:
            if old not in text:
                sys.exit(f"Expected text not found in {relative}: {old}")
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        print(f"changed {relative}")


def restore_ui():
    if not BACKUP.exists():
        sys.exit("Nothing to restore.")
    for relative in CHANGES:
        shutil.copy2(BACKUP / relative, ROOT / relative)
        print(f"restored {relative}")
    shutil.rmtree(BACKUP)


if __name__ == "__main__":
    actions = {"break": break_ui, "restore": restore_ui}
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        sys.exit(__doc__)
    actions[sys.argv[1]]()
