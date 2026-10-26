"""
Run this from the expense_tracker folder:   python check.py

It opens every page of the app using a TEMPORARY database (your real
expense.db is not touched) and tells you which file and line is wrong.
"""
import os
import sys
import tempfile
import traceback
from datetime import date

here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
sys.path.insert(0, here)

# Use a throw-away database
tmp = tempfile.mkdtemp()
os.environ["EXPENSE_DB"] = os.path.join(tmp, "check.db")

print("Folder:", here)
print()

# 1. Are all the files there?
needed = [
    "app.py", "static/app.css", "static/style.css",
    "templates/base.html", "templates/dashboard.html", "templates/budget.html",
    "templates/expense_form.html", "templates/history.html",
    "templates/reports.html", "templates/login.html", "templates/register.html",
    "templates/logged_out.html",
]
missing = [f for f in needed if not os.path.exists(os.path.join(here, f))]
if missing:
    print("MISSING FILES:", ", ".join(missing))
    print()

# 2. Is app.py the new version?
with open(os.path.join(here, "app.py"), encoding="utf-8") as f:
    source = f.read()
for marker in ["def budget_status", "def resolve_overspend", "CATEGORY_COLORS",
               "def budget(", "inject_colors"]:
    if marker not in source:
        print(f"app.py is OLD or incomplete: '{marker}' not found.")
        print("Replace the whole app.py with the new one.")
        sys.exit(1)

try:
    import app as m
except Exception:
    print("app.py could not start:")
    traceback.print_exc()
    sys.exit(1)

m.app.config["PROPAGATE_EXCEPTIONS"] = True
client = m.app.test_client()


def show_error(page):
    """Print the error and the template file/line where it happened."""
    exc_type, exc, tb = sys.exc_info()
    print(f"  FAILED: {page}")
    print(f"  Error : {exc_type.__name__}: {exc}")
    for frame in traceback.extract_tb(tb):
        if frame.filename.replace("\\", "/").endswith(".html") or \
                frame.filename.replace("\\", "/").endswith("/app.py"):
            print(f"  Where : {frame.filename}, line {frame.lineno}")
            if frame.line:
                print(f"          {frame.line.strip()}")
    print()


client.post("/register", data={"name": "checker", "password": "secret1",
                               "confirm_password": "secret1"})
client.post("/login", data={"name": "checker", "password": "secret1"})
client.post("/budget", data={"income": "30000", "savings": "5000",
                             "alert_percent": "80", "limit_Food": "1000"})
client.post("/add", data={"title": "Test", "amount": "1500", "category": "Food",
                          "expense_date": date.today().isoformat(), "note": ""})

pages = ["/dashboard", "/add", "/history", "/budget", "/reports"]
failed = 0
for page in pages:
    try:
        r = client.get(page)
        if r.status_code == 200:
            print(f"  OK     {page}")
        else:
            print(f"  FAILED {page} (status {r.status_code})")
            failed += 1
    except Exception:
        failed += 1
        show_error(page)

print()
if failed:
    print(f"{failed} page(s) failed. Copy the lines above and send them to me.")
else:
    print("All pages work. If the browser still shows an error, stop the server,")
    print("run python app.py again and press Ctrl+F5 in the browser.")
