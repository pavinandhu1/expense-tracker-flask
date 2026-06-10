from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "abc123"

# CREATE DATABASE
def init_db():

    with sqlite3.connect("task.dp") as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                amount REAL
            )
            """
        )

init_db()

@app.route("/", methods=["GET", "POST"])
def home():

    with sqlite3.connect("task.dp") as conn:

        cursor = conn.cursor()

        # ADD EXPENSE
        if request.method == "POST":

            expense = request.form["expense"]

            category = request.form["category"]

            amount = request.form["amount"]

            if expense and amount:

                cursor.execute(
                    """
                    INSERT INTO tasks(name, category, amount)
                    VALUES(?, ?, ?)
                    """,
                    (expense, category, amount)
                )

                conn.commit()

        # SEARCH + FILTER

        search = request.args.get("search", "")

        category_filter = request.args.get(
            "category_filter",
            ""
        )

        query = "SELECT * FROM tasks WHERE 1=1"

        params = []

        # SEARCH
        if search:

            query += " AND name LIKE ?"

            params.append(f"%{search}%")

        # CATEGORY FILTER
        if category_filter:

            query += " AND category=?"

            params.append(category_filter)

        cursor.execute(query, params)

        data = cursor.fetchall()

        # TOTAL
        cursor.execute(
            "SELECT SUM(amount) FROM tasks"
        )

        total = cursor.fetchone()[0] or 0

        # PIE CHART
        cursor.execute(
            """
            SELECT category, SUM(amount)
            FROM tasks
            GROUP BY category
            """
        )

        chart = cursor.fetchall()

        categories = [i[0] for i in chart]

        amounts = [i[1] for i in chart]

        # 🔥 SALARY + WARNING

        if request.args.get("salary"):
                session["salary"] = request.args.get("salary")

        salary = session.get("salary", "")

        warning = ""

        if salary:

            salary = float(salary)

            limit = salary * 0.8

            if total > limit:
                warning = (
                    "⚠ Warning: "
                    "Expenses crossed 80% of salary!"
                )


    return render_template(
        "index.html",
        data=data,
        total=total,
        categories=categories,
        amounts=amounts,
        search=search,
        category_filter=category_filter,
        salary=salary,
        warning=warning
    )

# DELETE
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    with sqlite3.connect("task.dp") as conn:

        conn.execute(
            "DELETE FROM tasks WHERE id=?",
            (id,)
        )

    return redirect("/")

# EDIT
@app.route("/edit/<int:id>")
def edit(id):

    conn = sqlite3.connect("task.dp")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (id,)
    )

    data = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        data=data
    )

# UPDATE
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    new_expense = request.form.get(
        "expense"
    )

    new_amount = request.form.get(
        "amount"
    )

    new_category = request.form.get(
        "category"
    )

    if new_expense.strip() and new_amount:

        conn = sqlite3.connect("task.dp")

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET name=?, amount=?, category=?
            WHERE id=?
            """,
            (
                new_expense,
                new_amount,
                new_category,
                id
            )
        )

        conn.commit()

        conn.close()

    return redirect("/")

if __name__ == "__main__":

    app.run(debug=True)