"""
Insta485 posts view.

URLs include: /posts/?target=URL
"""

import os
import pathlib
import uuid
import flask
import insta485


def upload_post(ownername):
    """Upload a post to insta485."""
    # Unpack flask object
    fileobj = flask.request.files["file"]
    # If a user tries to create a post with an empty file, then abort(400)
    if fileobj is None:
        flask.abort(400)
    filename = fileobj.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name is compatible
    # with the filesystem.
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    fileobj.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_basename)

    # Connect to database
    connection = insta485.model.get_db()
    # Add a new like into database
    connection.execute(
        'INSERT INTO posts(filename, owner) VALUES (?, ?)',
        (filename, ownername)
    )


def delete_post():
    """Delete a post from the database."""
    postid = flask.request.form.get('postid')
    logname = flask.session.get('username')
    connection = insta485.model.get_db()
    # Get the post ownername
    cur = connection.execute(
        "SELECT filename, owner "
        "FROM posts WHERE postid = ?",
        (postid, )
    )
    result = cur.fetchall()
    owner = result[0]['owner']
    # If a user tries to delete a post that they do not own, then abort(403)
    if owner != logname:
        flask.abort(403)

    # Delete everything in the database related to this post.
    file_path = insta485.app.config["UPLOAD_FOLDER"]/result[0]['filename']
    with open(file_path, encoding='ISO-8859-1', mode='r'):
        os.remove(file_path)
    connection.execute(
        "DELETE FROM posts WHERE postid = ?",
        (postid, )
    )


@insta485.app.route('/posts/', methods=['POST'])
def create_delete_posts():
    """Display the /posts/ route."""
    logname = flask.session['username']
    # If operation is create, save the image file to disk and redirect to URL
    # If operation is delete, delete the image file from the filesystem
    if flask.request.form.get('operation') == 'create':
        upload_post(logname)
        if 'target' in flask.request.args:
            return flask.redirect(flask.request.args.get('target'))
    elif flask.request.form.get('operation') == 'delete':
        delete_post()

    # Redirect to URL
    return flask.redirect('/users/' + logname + '/')
