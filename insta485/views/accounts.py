"""
Insta485 accounts view.

URLs include:
/accounts/login/
/accounts/logout/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
"""

import pathlib
import os
import uuid
import hashlib
import flask
import insta485


@insta485.app.route('/accounts/login/')
def login():
    """Implement GET login route method."""
    # If logged in, redirect to /.
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    context = {}
    return flask.render_template("login.html", **context)


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Implement POST logout route method."""
    # Log out user. Immediately redirect to /accounts/login/
    if 'username' in flask.session:
        flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/create/')
def create():
    """Implement GET create route method."""
    # If a user is already logged in, redirect to /accounts/edit/
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    context = {}
    return flask.render_template("create.html", **context)


@insta485.app.route('/accounts/delete/')
def delete():
    """Implement GET delete route method."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    username = flask.session['username']
    context = {'username': username}
    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/')
def edit():
    """Implement GET edit route method."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    # Get the logname, fullname, email and user img_url to fill the template
    cur = connection.execute(
        "SELECT username, fullname, email, filename "
        "FROM users WHERE username = ? ",
        (flask.session['username'], )
    )
    info = cur.fetchall()[0]
    context = {
        'logname': info['username'],
        'fullname': info['fullname'],
        'email': info['email'],
        'img_url': '/uploads/' + info['filename']
    }
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/')
def password_():
    """Implement GET password route method."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    logname = flask.session.get('username')
    context = {
        'logname': logname
    }
    return flask.render_template("password.html", **context)


# ----------------------------------------------------------------
# Define some operation functions for POST /accounts/ method
def login_op():
    """Log in operations."""
    # Use username and password from the POST request form content
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    # If the username or password fields are empty, abort(400)
    if username == '' or password == '':
        flask.abort(400)

    # Verify password against the user’s password hash in the database
    connection = insta485.model.get_db()
    cur = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE users.username = ?",
            (username, )
        )
    # If username authentication fails, abort(403)
    pas = cur.fetchall()
    if len(pas) == 0:
        flask.abort(403)
    pas = pas[0]['password']

    # Verify password (if it is not encoded) against the user input
    if "$" not in pas:
        if pas != password:
            flask.abort(403)
    else:
        salt = pas.split("$")[1]
        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        # If password authentication fails, abort(403)
        if password_db_string != pas:
            flask.abort(403)

    flask.session['username'] = username


def create_op():
    """Create operations."""
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files['file']

    if not username or not password or not fullname or not email:
        flask.abort(400)
    if fileobj.filename == '':
        flask.abort(400)

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT COUNT(1) AS user_exist_or_not "
        "FROM users WHERE username = ?",
        (username, )
    )
    if cur.fetchall()[0]['user_exist_or_not'] != 0:
        flask.abort(409)

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name is compatible with
    # the filesystem.
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(fileobj.filename).suffix
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    fileobj.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)

    # A password entry in the database contains the algorithm,
    # salt and password hash separated by $
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new('sha512')
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join(['sha512', salt, password_hash])

    cur = connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_basename, password_db_string)
    )

    flask.session['username'] = username


def delete_op():
    """Delete operations."""
    # If the user is not logged in, abort(403).
    if 'username' not in flask.session:
        flask.abort(403)
    # Connect to the database
    connection = insta485.model.get_db()
    # Delete user icon file
    cur = connection.execute(
        "SELECT filename FROM users "
        "WHERE username = ? ",
        (flask.session['username'], )
    )

    filepath = insta485.app.config['UPLOAD_FOLDER'] / \
        cur.fetchall()[0]['filename']
    with open(filepath, encoding='ISO-8859-1', mode='r'):
        os.remove(filepath)

    # Delete user's post files
    cur = connection.execute(
        "SELECT filename FROM posts "
        "WHERE owner = ?",
        (flask.session['username'], )
    )
    files = cur.fetchall()
    for file in files:
        filepath = insta485.app.config['UPLOAD_FOLDER']/file['filename']
        with open(filepath, encoding='ISO-8859-1', mode='r'):
            os.remove(filepath)

    # Delete the user and all things related to this user
    cur = connection.execute(
        "DELETE FROM users WHERE username = ?",
        (flask.session['username'], )
    )
    flask.session.clear()


def edit_op():
    """Edit account operations."""
    # If the user is not logged in, abort(403).
    if 'username' not in flask.session:
        flask.abort(403)
    # Connect to the database
    connection = insta485.model.get_db()

    # Use fullname, email and file from the POST request form content
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    # If the fullname or email fields are empty, abort(400)
    if not fullname or not email:
        flask.abort(400)
    # If no photo file is included, update only the user’s name and email.
    connection.execute(
        "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
        (fullname, email, flask.session['username'])
    )

    # Unpack flask object
    fileobj = flask.request.files["file"]
    filename = fileobj.filename
    # If a photo file is included, then the server will update the user’s photo
    if filename != '':
        # Compute base name (filename without directory).  We use a UUID to
        # avoid clashes with existing files, and ensure that the name is
        # compatible with the filesystem.
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{stem}{suffix}"
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        connection.execute(
            "UPDATE users SET filename = ? WHERE username = ?",
            (uuid_basename, flask.session['username'])
        )


def password_op():
    """Update password operations."""
    # If the user is not logged in, abort(403).
    if 'username' not in flask.session:
        flask.abort(403)
    # Connect to the database
    connection = insta485.model.get_db()

    # Use password, new_password1 and new_password2 from the POST request form
    password = flask.request.form.get('password')
    new_password1 = flask.request.form.get('new_password1')
    new_password2 = flask.request.form.get('new_password2')
    # If any of the above fields are empty, abort(400)
    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    # Verify password against the user’s password hash in the database
    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (flask.session['username'],)
    )
    real_password = cur.fetchall()[0]['password']

    if "$" in real_password:
        salt = real_password.split('$')[1]
        algorithm = 'sha512'
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        # If verification fails, abort(403)
        if password_db_string != real_password:
            flask.abort(403)
    else:
        if real_password != password:
            flask.abort(403)

    # Verify both new passwords match. If verification fails, abort(401)
    if new_password1 != new_password2:
        flask.abort(401)

    # Update hashed password entry in database
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + new_password1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    cur = connection.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (password_db_string, flask.session['username'])
    )


@insta485.app.route('/accounts/', methods=['POST'])
def accounts_operation():
    """Perform various account operations and immediately redirect to URL."""
    if flask.request.form.get('operation') == 'login':
        login_op()
    elif flask.request.form.get('operation') == 'create':
        create_op()
    elif flask.request.form.get('operation') == 'delete':
        delete_op()
    elif flask.request.form.get('operation') == 'edit_account':
        edit_op()
    elif flask.request.form.get('operation') == 'update_password':
        password_op()

    # Perform various account operations and immediately redirect to URL
    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    # If the value of ?target is not set, redirect to /.
    return flask.redirect(flask.url_for('show_index'))
