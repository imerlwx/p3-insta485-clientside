"""
Insta485 comments view.

URLs include: /comments/?target=URL
"""
import flask
import insta485


def create_comments():
    """Insert comments into the post."""
    comment_owner = flask.session.get('username')
    postid = flask.request.form.get('postid')
    text = flask.request.form['text']
    # If a user tries to create an empty comment, then abort(400)
    if len(text) == 0:
        flask.abort(400)
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (?, ?, ?)", (comment_owner, postid, text)
    )


def delete_comments():
    """Delete comments from the post."""
    logname = flask.session.get('username')
    commentid = flask.request.form['commentid']
    connection = insta485.model.get_db()
    # If a user tries to delete a comment that they do not own, then abort(403)
    cur = connection.execute(
        "SELECT owner FROM comments "
        "WHERE commentid = ?", (commentid, )
    )
    comment_owner = cur.fetchall()[0]['owner']
    if comment_owner != logname:
        flask.abort(403)

    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid = ?", (commentid, )
    )


@insta485.app.route('/comments/', methods=["POST"])
def comments_request():
    """Display the /comments/ route."""
    # If operation is create, create a new comment on postid with the content
    # If operation is delete, delete comment with ID commentid
    if flask.request.form.get('operation') == 'create':
        create_comments()
    elif flask.request.form.get('operation') == 'delete':
        delete_comments()

    # If the value of ?target is not set, redirect to /
    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_index'))
