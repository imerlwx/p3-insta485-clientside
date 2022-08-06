"""
Insta485 likes view.

URLs include: /likes/?target=URL
"""

import flask
import insta485


def like():
    """Create a like for postid."""
    # Need the username and postid to locate the post and like
    username = flask.session.get('username')
    postid = flask.request.form.get('postid')
    # Connect to database
    connection = insta485.model.get_db()
    # Add a new like into database
    connection.execute(
        'INSERT INTO likes (owner, postid) VALUES (?, ?)',
        (username, postid)
    )


def unlike():
    """Delete a like for postid."""
    username = flask.session.get('username')
    postid = flask.request.form.get('postid')
    connection = insta485.model.get_db()
    connection.execute(
        'DELETE FROM likes WHERE owner = ? AND postid = ?',
        (username, postid)
    )


@insta485.app.route('/likes/', methods=["POST"])
def like_unlike_request():
    """Display the /likes/ route."""
    connection = insta485.model.get_db()
    postid = flask.request.form.get('postid')
    logname = flask.session['username']
    # Get the attitude of the login user of the post
    cur = connection.execute(
        "SELECT COUNT(1) AS like_or_not FROM likes "
        "WHERE likes.postid = ? AND likes.owner = ? ",
        (postid, logname, )
    )
    login_user_like_or_not = cur.fetchall()
    # If operation is like, create a like for postid.
    # If operation is unlike, delete a like for postid.
    if flask.request.form.get('operation') == 'like':
        if login_user_like_or_not[0]['like_or_not'] != 0:
            flask.abort(409)
        like()
    elif flask.request.form.get('operation') == 'unlike':
        if login_user_like_or_not[0]['like_or_not'] == 0:
            flask.abort(409)
        unlike()

    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_index'))
