from flask import render_template, request, redirect, url_for

from . import app
from . database import session, Entry

PAGINATE_BY = 10

@app.route("/", methods=["POST","GET"])
@app.route("/page/<int:page>", methods=["POST","GET"])
def entries(PAGINATE_BY = PAGINATE_BY, page = 1):
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

    with app.request_context(environ):
        paginate = request.form["paginate"]


    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        PAGINATE_BY=PAGINATE_BY,
        total_pages=total_pages,
        paginate=paginate
    )

@app.route("/entry/<int:id>")
def view_entry(id):
    entry = session.query(Entry).filter(Entry.id==id + 1)

    page_index = id - 1

    count = session.query(Entry).count()

    total_pages = (count - 1)
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    return render_template("entry.html",
                           entry=entry,
                           has_next=has_next,
                           has_prev=has_prev,
                           id=id,
                           total_pages=total_pages,
                           )


@app.route("/entry/add", methods=["GET"])
def add_entry_get():
    return render_template("add_entry.html")

@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<int:id>/edit", methods=["GET"])
def edit_entry_get(id):
    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    return render_template("edit_entry.html",
                           entry=entry,
                           id=id)

@app.route("/entry/<int:id>/edit", methods=["POST"])
def edit_entry_post(id):

    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    entry.title = request.form["title"]
    entry.content = request.form["content"]

    session.add(entry)
    session.commit()

    return redirect(url_for("entries"))


@app.route("/entry/<int:id>/delete", methods=["GET"])
def get_delete_entry(id):
    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    return render_template("entry_delete.html",
                           id=id,
                           entry=entry)

@app.route("/entry/<int:id>/delete", methods=["POST"])
def delete_entry_delete(id):

    entry = session.query(Entry).filter(Entry.id == id + 1).all()[0]

    session.delete(entry)
    session.commit()

    return redirect(url_for("entries"))


@app.route("/paging", methods=["GET"])
def paging_get():
    return render_template("paging.html")

@app.route("/paging", methods=["POST"])
def paging_post():
    return render_template("entries.html",
                           PAGINATE_BY = request.form["paginate"])

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")