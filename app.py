from datetime import date
from functools import wraps
import math
import os
import sqlite3

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "my_expense_tracker_secret_key")

# Always keep the database next to app.py, wherever the app is started from
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("EXPENSE_DB", os.path.join(BASE_DIR, "expense.db"))

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Health", "Entertainment", "Education", "Other",
]

# One colour per category, used on every page
CATEGORY_COLORS = {
    "Food": "#e76f51",
    "Transport": "#2a9d8f",
    "Shopping": "#6d597a",
    "Bills": "#264653",
    "Health": "#b56576",
    "Entertainment": "#f4a261",
    "Education": "#e9c46a",
    "Other": "#8d99ae",
}


@app.context_processor
def inject_colors():
    return {"CATEGORY_COLORS": CATEGORY_COLORS}


# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(conn, table, column, definition):
    columns = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def create_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # New columns for existing databases (safe to run every time)
    add_column_if_missing(conn, "users", "monthly_income", "REAL NOT NULL DEFAULT 0")
    add_column_if_missing(conn, "users", "savings", "REAL NOT NULL DEFAULT 0")
    add_column_if_missing(conn, "users", "alert_percent", "INTEGER NOT NULL DEFAULT 80")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Monthly spending limit for each category
    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            limit_amount REAL NOT NULL,
            UNIQUE (user_id, category),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Records of overspending being covered, for one month at a time.
    # source_type is 'savings' or 'category'.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS budget_adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            category TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_category TEXT,
            amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


# Create tables when the app is loaded (also works on hosting services)
create_database()


# ---------------- LOGIN REQUIRED ----------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------------- HELPERS ----------------

def month_key(d=None):
    return (d or date.today()).strftime("%Y-%m")


def parse_money(raw):
    """Empty -> 0.0. Raises ValueError for bad, negative or non-finite numbers."""
    raw = (raw or "").strip()
    if not raw:
        return 0.0
    value = float(raw)
    if not math.isfinite(value) or value < 0:
        raise ValueError("invalid amount")
    return round(value, 2)


def validate_expense_form(form):
    """Returns (data, error). data is a tuple ready for the database."""
    title = form.get("title", "").strip()
    category = form.get("category", "")
    expense_date = form.get("expense_date", "")
    note = form.get("note", "").strip()

    try:
        amount = float(form.get("amount", ""))
    except ValueError:
        return None, "Enter a valid amount."

    if not math.isfinite(amount):
        return None, "Enter a valid amount."
    if not title or not expense_date:
        return None, "Title and date are required."
    try:
        date.fromisoformat(expense_date)
    except ValueError:
        return None, "Enter a valid date."
    if amount <= 0:
        return None, "Amount must be greater than zero."
    if category not in CATEGORIES:
        return None, "Choose a valid category."

    return (title, round(amount, 2), category, expense_date, note), None


def budget_status(conn, user_id, month):
    """Spending, limits and alert state for every category in one month.

    effective limit = base limit
                      + money moved in (from savings or another category)
                      - money moved out to another category
    state: 'none' (no limit set), 'ok', 'warn' (reached the alert %), 'over'
    """
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    threshold = user["alert_percent"] or 80

    limits = {
        r["category"]: r["limit_amount"]
        for r in conn.execute(
            "SELECT category, limit_amount FROM budgets WHERE user_id = ?",
            (user_id,))
    }

    spent = {
        r["category"]: r["total"]
        for r in conn.execute(
            """SELECT category, SUM(amount) AS total FROM expenses
               WHERE user_id = ? AND substr(expense_date, 1, 7) = ?
               GROUP BY category""",
            (user_id, month))
    }

    added, removed, covered = {}, {}, 0.0
    for a in conn.execute(
            "SELECT * FROM budget_adjustments WHERE user_id = ? AND month = ?",
            (user_id, month)):
        added[a["category"]] = added.get(a["category"], 0.0) + a["amount"]
        if a["source_type"] == "category":
            src = a["source_category"]
            removed[src] = removed.get(src, 0.0) + a["amount"]
        else:
            covered += a["amount"]

    rows = []
    for cat in CATEGORIES:
        spent_c = spent.get(cat, 0.0)
        row = {
            "category": cat,
            "color": CATEGORY_COLORS[cat],
            "spent": spent_c,
            "limit": None,
            "remaining": None,
            "percent": 0.0,
            "over": 0.0,
            "state": "none",
        }
        base = limits.get(cat)
        if base:
            limit = base + added.get(cat, 0.0) - removed.get(cat, 0.0)
            remaining = limit - spent_c
            percent = spent_c / limit * 100 if limit > 0 else 100.0
            if remaining < -0.005:
                state = "over"
            elif percent >= threshold:
                state = "warn"
            else:
                state = "ok"
            row.update(limit=limit, remaining=remaining, percent=percent,
                       over=max(0.0, -remaining), state=state)
        rows.append(row)

    return {
        "user": user,
        "rows": rows,
        "total_spent": sum(spent.values()),
        "covered": covered,
        "threshold": threshold,
    }


def budget_alert_message(conn, user_id, category, expense_date):
    """Warning text if this category is near/over its limit this month."""
    if expense_date[:7] != month_key():
        return None

    status = budget_status(conn, user_id, month_key())
    row = next((r for r in status["rows"] if r["category"] == category), None)
    if row is None:
        return None

    if row["state"] == "over":
        return (f"{category} is over its budget by ₹{row['over']:.2f}. "
                "Open the Dashboard to choose how to cover it.")
    if row["state"] == "warn":
        return (f"{category} has used {row['percent']:.0f}% of its budget "
                f"(₹{row['remaining']:.2f} left).")
    return None


# ---------------- HOME ----------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not name or not password or not confirm_password:
            flash("Please fill all the fields.")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, password) VALUES (?, ?)",
                (name, hashed_password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            flash("Username already exists. Please choose another name.")
            return redirect(url_for("register"))

        conn.close()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        name = request.form["name"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE name = ?", (name,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Invalid name or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    name = session.get("user_name", "")
    session.clear()
    return render_template("logged_out.html", name=name)


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    month = month_key()
    conn = get_db_connection()

    status = budget_status(conn, user_id, month)
    user = status["user"]
    rows = status["rows"]

    income = user["monthly_income"]
    savings = user["savings"]

    # Salary left = income - spending this month,
    # plus any overspend that was covered from savings instead
    balance = income - status["total_spent"] + status["covered"]

    all_time_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    recent = conn.execute(
        """SELECT * FROM expenses WHERE user_id = ?
           ORDER BY expense_date DESC, id DESC LIMIT 5""",
        (user_id,)
    ).fetchall()

    conn.close()

    alert_rows = [r for r in rows if r["state"] in ("warn", "over")]

    # Over-budget categories, each with the ways it can be covered
    over_rows = []
    for r in rows:
        if r["state"] != "over":
            continue
        options = []
        if savings > 0.005:
            options.append({
                "value": "savings",
                "label": f"Savings (₹{savings:.2f} available)",
            })
        for s in rows:
            if (s["category"] != r["category"] and s["limit"]
                    and s["remaining"] > 0.005):
                options.append({
                    "value": "cat:" + s["category"],
                    "label": (f"Reduce {s['category']} budget "
                              f"(₹{s['remaining']:.2f} spare)"),
                })
        over_rows.append({**r, "options": options})

    return render_template(
        "dashboard.html",
        month_label=date.today().strftime("%B %Y"),
        income=income,
        savings=savings,
        spent=status["total_spent"],
        balance=balance,
        all_time_total=all_time_total,
        rows=rows,
        alert_rows=alert_rows,
        over_rows=over_rows,
        recent=recent,
    )


# ---------------- BUDGET SETTINGS ----------------

@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    user_id = session["user_id"]
    conn = get_db_connection()

    if request.method == "POST":
        try:
            income = parse_money(request.form.get("income"))
            savings = parse_money(request.form.get("savings"))
            alert_percent = int(request.form.get("alert_percent") or 80)

            limits = {}
            for c in CATEGORIES:
                value = parse_money(request.form.get("limit_" + c))
                if value > 0:
                    limits[c] = value
        except ValueError:
            conn.close()
            flash("Enter valid, non-negative numbers.", "warning")
            return redirect(url_for("budget"))

        if not 1 <= alert_percent <= 100:
            conn.close()
            flash("Alert percentage must be between 1 and 100.", "warning")
            return redirect(url_for("budget"))

        conn.execute(
            """UPDATE users SET monthly_income = ?, savings = ?,
               alert_percent = ? WHERE id = ?""",
            (income, savings, alert_percent, user_id)
        )

        for c in CATEGORIES:
            if c in limits:
                conn.execute(
                    """INSERT INTO budgets (user_id, category, limit_amount)
                       VALUES (?, ?, ?)
                       ON CONFLICT (user_id, category)
                       DO UPDATE SET limit_amount = excluded.limit_amount""",
                    (user_id, c, limits[c])
                )
            else:
                conn.execute(
                    "DELETE FROM budgets WHERE user_id = ? AND category = ?",
                    (user_id, c)
                )

        conn.commit()
        conn.close()

        flash("Budget saved.")
        total_budgeted = sum(limits.values())
        if income and total_budgeted > income:
            flash(f"Your category budgets add up to ₹{total_budgeted:.2f}, "
                  f"which is more than your income of ₹{income:.2f}.",
                  "warning")
        return redirect(url_for("budget"))

    month = month_key()
    status = budget_status(conn, user_id, month)

    limits = {
        r["category"]: r["limit_amount"]
        for r in conn.execute(
            "SELECT category, limit_amount FROM budgets WHERE user_id = ?",
            (user_id,))
    }

    adjustments = []
    for a in conn.execute(
            """SELECT * FROM budget_adjustments
               WHERE user_id = ? AND month = ? ORDER BY id DESC""",
            (user_id, month)):
        source = "Savings" if a["source_type"] == "savings" else a["source_category"]
        adjustments.append({
            "id": a["id"],
            "category": a["category"],
            "amount": a["amount"],
            "source": source,
        })

    conn.close()

    user = status["user"]
    return render_template(
        "budget.html",
        categories=CATEGORIES,
        limits=limits,
        income=user["monthly_income"],
        savings=user["savings"],
        alert_percent=user["alert_percent"],
        total_budgeted=sum(limits.values()),
        adjustments=adjustments,
        month_label=date.today().strftime("%B %Y"),
    )


# ---------------- COVER AN OVERSPEND ----------------

@app.route("/budget/resolve", methods=["POST"])
@login_required
def resolve_overspend():
    user_id = session["user_id"]
    category = request.form.get("category", "")
    source = request.form.get("source", "")

    try:
        amount = round(float(request.form.get("amount", "")), 2)
    except ValueError:
        flash("Enter a valid amount.", "warning")
        return redirect(url_for("dashboard"))

    month = month_key()
    conn = get_db_connection()
    status = budget_status(conn, user_id, month)
    rows = {r["category"]: r for r in status["rows"]}
    savings = status["user"]["savings"]

    row = rows.get(category)
    error = None

    if row is None or row["state"] != "over":
        error = "That category is not over budget."
    elif not math.isfinite(amount) or amount <= 0 or amount > row["over"] + 0.005:
        error = f"Enter an amount up to ₹{row['over']:.2f}."
    elif source == "savings":
        if amount > savings + 0.005:
            error = f"You only have ₹{savings:.2f} in savings."
    elif source.startswith("cat:"):
        src = rows.get(source[4:])
        if src is None or src["category"] == category or not src["limit"]:
            error = "Choose a different category to take the money from."
        elif amount > src["remaining"] + 0.005:
            error = (f"{src['category']} only has ₹{max(src['remaining'], 0):.2f} "
                     "of budget left.")
    else:
        error = "Choose where the money should come from."

    if error:
        conn.close()
        flash(error, "warning")
        return redirect(url_for("dashboard"))

    if source == "savings":
        conn.execute(
            """INSERT INTO budget_adjustments
               (user_id, month, category, source_type, source_category, amount)
               VALUES (?, ?, ?, 'savings', NULL, ?)""",
            (user_id, month, category, amount)
        )
        conn.execute(
            "UPDATE users SET savings = ROUND(savings - ?, 2) WHERE id = ?",
            (amount, user_id)
        )
        message = f"₹{amount:.2f} for {category} was taken from your savings."
    else:
        src_name = source[4:]
        conn.execute(
            """INSERT INTO budget_adjustments
               (user_id, month, category, source_type, source_category, amount)
               VALUES (?, ?, ?, 'category', ?, ?)""",
            (user_id, month, category, src_name, amount)
        )
        message = (f"₹{amount:.2f} moved from the {src_name} budget "
                   f"to {category}.")

    conn.commit()
    conn.close()

    flash(message)
    return redirect(url_for("dashboard"))


@app.route("/budget/undo/<int:adjustment_id>", methods=["POST"])
@login_required
def undo_adjustment(adjustment_id):
    user_id = session["user_id"]
    conn = get_db_connection()

    adj = conn.execute(
        "SELECT * FROM budget_adjustments WHERE id = ? AND user_id = ?",
        (adjustment_id, user_id)
    ).fetchone()

    if adj is not None:
        if adj["source_type"] == "savings":
            conn.execute(
                "UPDATE users SET savings = ROUND(savings + ?, 2) WHERE id = ?",
                (adj["amount"], user_id)
            )
        conn.execute(
            "DELETE FROM budget_adjustments WHERE id = ? AND user_id = ?",
            (adjustment_id, user_id)
        )
        conn.commit()
        flash("Adjustment undone.")

    conn.close()
    return redirect(url_for("budget"))


# ---------------- ADD EXPENSE ----------------

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():

    if request.method == "POST":
        data, error = validate_expense_form(request.form)

        if error:
            flash(error)
            return redirect(url_for("add_expense"))

        conn = get_db_connection()
        conn.execute(
            """INSERT INTO expenses
               (user_id, title, amount, category, expense_date, note)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session["user_id"], *data)
        )
        conn.commit()
        alert = budget_alert_message(conn, session["user_id"], data[2], data[3])
        conn.close()

        flash("Expense added.")
        if alert:
            flash(alert, "warning")
        return redirect(url_for("history"))

    return render_template(
        "expense_form.html",
        categories=CATEGORIES,
        expense=None,
        today=date.today().isoformat(),
    )


# ---------------- EDIT EXPENSE ----------------

@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    conn = get_db_connection()

    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    ).fetchone()

    if expense is None:
        conn.close()
        flash("Expense not found.")
        return redirect(url_for("history"))

    if request.method == "POST":
        data, error = validate_expense_form(request.form)

        if error:
            conn.close()
            flash(error)
            return redirect(url_for("edit_expense", expense_id=expense_id))

        conn.execute(
            """UPDATE expenses
               SET title = ?, amount = ?, category = ?,
                   expense_date = ?, note = ?
               WHERE id = ? AND user_id = ?""",
            (*data, expense_id, session["user_id"])
        )
        conn.commit()
        alert = budget_alert_message(conn, session["user_id"], data[2], data[3])
        conn.close()

        flash("Expense updated.")
        if alert:
            flash(alert, "warning")
        return redirect(url_for("history"))

    conn.close()
    return render_template(
        "expense_form.html",
        categories=CATEGORIES,
        expense=expense,
        today=date.today().isoformat(),
    )


# ---------------- DELETE EXPENSE ----------------

@app.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    flash("Expense deleted.")
    return redirect(url_for("history"))


# ---------------- HISTORY (DATE-WISE) ----------------

@app.route("/history")
@login_required
def history():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    category = request.args.get("category", "")

    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [session["user_id"]]

    if start:
        query += " AND expense_date >= ?"
        params.append(start)
    if end:
        query += " AND expense_date <= ?"
        params.append(end)
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY expense_date DESC, id DESC"

    conn = get_db_connection()
    expenses = conn.execute(query, params).fetchall()
    conn.close()

    # Group by date
    grouped = {}
    for e in expenses:
        grouped.setdefault(e["expense_date"], []).append(e)

    filtered_total = sum(e["amount"] for e in expenses)

    return render_template(
        "history.html",
        grouped=grouped,
        filtered_total=filtered_total,
        categories=CATEGORIES,
        start=start,
        end=end,
        selected_category=category,
    )


# ---------------- CHARTS & REPORTS ----------------

@app.route("/reports")
@login_required
def reports():
    user_id = session["user_id"]
    conn = get_db_connection()

    category_rows = conn.execute(
        """SELECT category, SUM(amount) AS total FROM expenses
           WHERE user_id = ? GROUP BY category ORDER BY total DESC""",
        (user_id,)
    ).fetchall()

    monthly_rows = conn.execute(
        """SELECT substr(expense_date, 1, 7) AS month, SUM(amount) AS total
           FROM expenses WHERE user_id = ?
           GROUP BY month ORDER BY month""",
        (user_id,)
    ).fetchall()

    status = budget_status(conn, user_id, month_key())

    conn.close()

    budget_rows = [r for r in status["rows"] if r["limit"]]

    # Share of total spending (all time) for each category, plus
    # how much of this month's income has been spent
    grand_total = sum(r["total"] for r in category_rows)
    breakdown = [
        {
            "category": r["category"],
            "color": CATEGORY_COLORS.get(r["category"], "#8d99ae"),
            "total": r["total"],
            "percent": (r["total"] / grand_total * 100) if grand_total else 0.0,
        }
        for r in category_rows
    ]
    income = status["user"]["monthly_income"]
    month_spent = status["total_spent"]
    income_used_percent = (month_spent / income * 100) if income else None

    # Doughnut chart drawn as SVG circles (circumference = 100, so a
    # slice's length is simply its percentage)
    donut = []
    cumulative = 0.0
    for b in breakdown:
        p = b["percent"]
        mid = (cumulative + p / 2) / 100 * 2 * math.pi - math.pi / 2
        donut.append({
            **b,
            "dash": round(p, 3),
            "gap": round(100 - p, 3),
            "offset": round(25 - cumulative, 3),
            "tx": round(21 + 15.9155 * math.cos(mid), 2),
            "ty": round(21 + 15.9155 * math.sin(mid) + 1, 2),
            "show_label": p >= 4,
        })
        cumulative += p

    # Monthly bars (height is a percentage of the biggest month)
    biggest = max([r["total"] for r in monthly_rows] or [1]) or 1
    months = [
        {
            "label": r["month"],
            "total": r["total"],
            "height": round(r["total"] / biggest * 100, 1),
        }
        for r in monthly_rows
    ]

    # Budget vs spent for this month
    budget_bars = [
        {
            "category": r["category"],
            "color": r["color"],
            "spent": r["spent"],
            "limit": r["limit"],
            "percent": min(r["percent"], 100),
            "state": r["state"],
        }
        for r in budget_rows
    ]

    return render_template(
        "reports.html",
        has_data=bool(category_rows),
        donut=donut,
        months=months,
        budget_bars=budget_bars,
        breakdown=breakdown,
        grand_total=grand_total,
        income=income,
        month_spent=month_spent,
        income_used_percent=income_used_percent,
        monthly_rows=monthly_rows,
        month_label=date.today().strftime("%B %Y"),
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
