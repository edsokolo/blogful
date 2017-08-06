from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash

from . import app
from . database import session, Entry, User

PAGINATE_BY = 10

@app.route("/", methods=["GET"])
@app.route("/page/<int:page>", methods=["POST","GET"])
def entries(PAGINATE_BY = PAGINATE_BY, page = 1):
    logged_in = current_user.is_authenticated
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]


    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        PAGINATE_BY=PAGINATE_BY,
        total_pages=total_pages,
        logged_in=logged_in,
    )

@app.route("/entry/<int:id>")
def view_entry(id):
    logged_in = current_user.is_authenticated
    entry = session.query(Entry).filter(Entry.id==id + 1)

    page_index = id - 1

    count = session.query(Entry).count()

    total_pages = (count - 1)
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    return render_template("entry.html",
                           entry=entry,
                           id=id,
                           has_next=has_next,
                           has_prev=has_prev,
                           total_pages=total_pages,
                           logged_in=logged_in
                           )


@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    logged_in = current_user.is_authenticated
    return render_template("add_entry.html",
                           logged_in=logged_in,)

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    logged_in = current_user.is_authenticated
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user,
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<int:id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    logged_in = current_user.is_authenticated

    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    return render_template("edit_entry.html",
                           entry=entry,
                           id=id,
                           logged_in=logged_in,)

@app.route("/entry/<int:id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    logged_in = current_user.is_authenticated
    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    entry.title = request.form["title"]
    entry.content = request.form["content"]

    session.add(entry)
    session.commit()

    return redirect(url_for("entries"))


@app.route("/entry/<int:id>/delete", methods=["GET"])
@login_required
def get_delete_entry(id):
    logged_in = current_user.is_authenticated
    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    return render_template("entry_delete.html",
                           id=id,
                           entry=entry,
                           logged_in=logged_in,)

@app.route("/entry/<int:id>/delete", methods=["POST"])
@login_required
def delete_entry_delete(id):
    logged_in = current_user.is_authenticated
    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    session.delete(entry)
    session.commit()

    return redirect(url_for("entries"))


@app.route("/paging", methods=["GET"])
def paging_get():
    logged_in = current_user.is_authenticated
    return render_template("paging.html",
                           logged_in=logged_in,)

@app.route("/paging", methods=["POST"])
def paging_post():
    logged_in = current_user.is_authenticated
    return render_template("entries.html",
                           PAGINATE_BY = request.form["paginate"])

@app.route("/login", methods=["GET"])
def login_get():
    logged_in = current_user.is_authenticated
    return render_template("login.html",
                               logged_in=logged_in,)

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    logged_in = current_user.is_authenticated
    return redirect(request.args.get('previous') or request.args.get('next') or url_for("entries"))

@app.route("/logout", methods=["GET"])
def logout_get():
    logout_user()
    logged_in = current_user.is_authenticated
    return redirect(request.referrer)