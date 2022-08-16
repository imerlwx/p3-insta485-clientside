"""REST API for comments."""
import flask
import insta485
from insta485.api.util import error_checking, wrong_password, invalid_postid


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comments():
    """Create a new comment to a post."""
    # Make sure HTTP Basic Authentication works
    if not flask.request.authorization and 'username' not in flask.session:
        return flask.jsonify(**error_checking(403)), 403

    if not flask.request.authorization:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if wrong_password(username, password):
            return flask.jsonify(**error_checking(403)), 403

    # Check if the postid_url_slug is valid
    postid = int(flask.request.args.get('postid'))
    if invalid_postid(postid):
        return flask.jsonify(**error_checking(404)), 404

    text = flask.request.json["text"]
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO comments (owner, postid, text) "
        "VALUES (?, ?, ?)", (username, postid, text, )
    )

    # Get the inserted commentid
    cur = connection.execute("SELECT last_insert_rowid() AS commentid")
    commentid = cur.fetchall()[0]['commentid']
    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": "/users/" + username + "/",
        "text": text,
        "url": flask.request.path + str(commentid) + "/",
    }
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comments(commentid):
    """Delete a comment, including the ID of the comment in the URL."""
    # Make sure HTTP Basic Authentication works
    if not flask.request.authorization and 'username' not in flask.session:
        return flask.jsonify(**error_checking(403)), 403

    if not flask.request.authorization:
        username = flask.session['username']
    else:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        if wrong_password(username, password):
            return flask.jsonify(**error_checking(403)), 403

    connection = insta485.model.get_db()
    # If a user tries to delete a comment that they do not own, then abort(403)
    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?", (commentid, )
    )
    comment_owner = cur.fetchall()
    # If the commentid does not exist, return 404.
    if len(comment_owner) == 0:
        return flask.jsonify(**error_checking(404)), 404
    # If the user doesn’t own the comment, return 403.
    if comment_owner[0]['owner'] != username:
        return flask.jsonify(**error_checking(403)), 403

    connection.execute(
        "DELETE FROM comments WHERE commentid = ?", (commentid, )
    )
    context = {}
    # Return 204 on successfully deleting a comment
    return flask.jsonify(**context), 204
