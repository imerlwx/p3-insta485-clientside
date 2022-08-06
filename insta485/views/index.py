"""
Insta485 index (main) view.

URLs include:
/
"""

import os
import flask
import arrow
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    logname = flask.session.get('username')
    # logname = "awdeorio"

    # Connect to database
    connection = insta485.model.get_db()

    # get followers from each user
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (logname,)
    )
    users = cur.fetchall()

    # put the login user to the users table and put them into a list
    users.append({'username2': logname})
    new_user = []
    for user in users:
        new_user.append(user['username2'])

    if len(tuple(users)) == 1:
        cur = connection.execute(
            """ SELECT posts.postid, posts.owner,
                posts.filename AS img_url, posts.created AS timestamp,
                users.filename AS owner_img_url
                FROM posts JOIN users
                ON posts.owner = users.username AND users.username = ?
                ORDER BY posts.postid DESC;
            """, (tuple(new_user)[0], )
        )
    else:
        cur = connection.execute(
            """ SELECT posts.postid, posts.owner,
                posts.filename AS img_url, posts.created AS timestamp,
                users.filename AS owner_img_url
                FROM posts JOIN users
                ON posts.owner = users.username AND users.username IN {}
                ORDER BY posts.postid DESC;
                """.format(tuple(new_user))
        )

    posts = cur.fetchall()

    context = {}
    context['posts'] = []
    for post in posts:
        # a post is consisted of postid, owner, owner_img_url, img_url,
        # timestamp, likes, and comments (owner and text)
        # postid, owner, owner_img_url, img_url are already in the post dict
        post['img_url'] = '/uploads/' + post['img_url']
        post['owner_img_url'] = '/uploads/' + post['owner_img_url']
        post['timestamp'] = arrow.get(post['timestamp']).humanize()

        # Figure out whether the log in user likes this post
        cur = connection.execute(
            "SELECT COUNT(1) AS like_or_not "
            "FROM likes "
            "WHERE likes.postid = ? "
            "AND likes.owner = ?",
            (post['postid'], logname)
        )
        login_user_like_or_not = cur.fetchall()
        post['like_or_not'] = login_user_like_or_not[0]['like_or_not']

        # Get the number of likes of the post
        cur = connection.execute(
            "SELECT COUNT(1) AS likes_count "
            "FROM likes "
            "WHERE postid = ?",
            (post['postid'], )
        )
        for like in cur:
            post['likes'] = (like['likes_count'])

        # Get the comment details of the post
        cur = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE postid = ?",
            (post['postid'], )
        )
        comments = cur.fetchall()
        post['comments'] = comments

        context['posts'].append(post)

    # Add database info to context
    context['logname'] = logname
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    """Display /uploads/ route."""
    if 'username' not in flask.session:
        flask.abort(403)

    if not os.path.isfile(insta485.app.config['UPLOAD_FOLDER']/filename):
        flask.abort(404)

    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename, as_attachment=True)
