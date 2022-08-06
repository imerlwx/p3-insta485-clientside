"""
Insta485 POST follow view.

URLs include: /following/?target=URL
"""

import flask
import insta485


def follow(logname, username):
    """Login user could follow a user with given username."""
    # Connect to database
    connection = insta485.model.get_db()
    # Add a new like into database
    connection.execute(
        'INSERT INTO following(username1, username2) VALUES (?, ?)',
        (logname, username)
    )


def unfollow(logname, username):
    """Unfollow a user with username."""
    connection = insta485.model.get_db()
    connection.execute(
        'DELETE FROM following WHERE username1 = ? AND username2 = ?',
        (logname, username)
    )


@insta485.app.route('/following/', methods=['POST'])
def follow_unfollow_request():
    """Display the /following/ route."""
    connection = insta485.model.get_db()
    username = flask.request.form['username']
    logname = flask.session['username']
    # Get the attitude of the login user of the post
    cur = connection.execute(
        "SELECT COUNT(1) AS follow_or_not "
        "FROM following WHERE username1 = ? AND username2 = ? ",
        (logname, username, )
    )
    login_user_follow_or_not = cur.fetchall()
    # If operation is follow, then make user logname follow user username
    # If operation is unfollow, then make user logname unfollow user username
    if flask.request.form.get('operation') == 'follow':
        if login_user_follow_or_not[0]['follow_or_not'] != 0:
            flask.abort(409)
        follow(logname, username)
    elif flask.request.form.get('operation') == 'unfollow':
        if login_user_follow_or_not[0]['follow_or_not'] != 1:
            flask.abort(409)
        unfollow(logname, username)

    # If the value of ?target is not set, redirect to /
    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_index'))
