"""Status checking including error and password."""
import hashlib
import insta485
import flask


def error_checking(status_code):
    """Check status error."""
    if status_code == 400:
        message = "Bad Request"
    elif status_code == 401:
        message = "Unauthorized access"
    elif status_code == 403:
        message = "Forbidden"
    elif status_code == 404:
        message = "Not Found"
    elif status_code == 409:
        message = "Conflict"
    context = {
        "message": message,
        "status_code": status_code,
    }
    return context


def wrong_password(username, password):
    """Check password whether it is invalid(return True)."""
    connection = insta485.model.get_db()
    cur = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE users.username = ?",
            (username, )
        )
    # If username authentication fails, abort(403)
    pas = cur.fetchall()[0]['password']

    # Verify password (if it is not encoded) against the user input
    if "$" not in pas:
        return pas != password

    salt = pas.split("$")[1]
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # If password authentication fails, abort(403)
    return password_db_string != pas


def invalid_postid(postid):
    """Verify if the postid is invalid(return True)."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT max(postid) as max_postid FROM posts"
    )
    max_postid = int(cur.fetchall()[0]['max_postid'])
    return max_postid < postid

def check_auth(username):
    """Check the username and password."""
    if not flask.request.authorization and 'username' not in flask.session:
        return flask.jsonify(**error_checking(403)), 403

    if not flask.request.authorization:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if wrong_password(username, password):
            return flask.jsonify(**error_checking(403)), 403
