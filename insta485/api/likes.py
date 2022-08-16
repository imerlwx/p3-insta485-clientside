"""REST API for likes."""
import flask
import insta485
from insta485.api.util import error_checking, wrong_password, invalid_postid


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_likes():
    """Create one like for a specific post."""
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

    # Connect to database
    connection = insta485.model.get_db()

    # Check if the like already exists, if so return a 200 response
    cur = connection.execute(
        "SELECT count(1), likeid FROM likes WHERE owner = ? AND postid = ?",
        (username, postid, )
    )
    like_or_not = cur.fetchall()[0]['count(1)']
    if like_or_not:
        likeid = cur.fetchall()[0]['likeid']
        context = {
            "likeid": likeid,
            "url": "/api/v1/likes/" + str(likeid) + "/",
        }
        return flask.jsonify(**context), 201

    # Add a new like into database, return 201 on success
    connection.execute(
        'INSERT INTO likes (owner, postid) VALUES (?, ?)',
        (username, postid, )
    )
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
        (username, postid, )
    )
    likeid = cur.fetchall()[0]['likeid']
    context = {
        "likeid": likeid,
        "url": "/api/v1/likes/" + str(likeid) + "/",
    }
    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/likes/<int:likeid>', methods=['DELETE'])
def delete_likes(likeid):
    """Delete a like from the database."""
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
    cur = connection.execute(
        "SELECT owner FROM likes WHERE likeid = ?", (likeid, )
    )
    likes_owner = cur.fetchall()[0]['owner']
    # If the likeid does not exist, return 404.
    if likes_owner is None:
        return flask.jsonify(**error_checking(404)), 404
    # If the user does not own the like, return 403.
    if likes_owner != username:
        return flask.jsonify(**error_checking(403)), 403

    connection.execute(
        'DELETE FROM likes WHERE likeid = ?', (likeid, )
    )
    context = {}
    # Return 204 on successfully delete a like
    return flask.jsonify(**context), 204
