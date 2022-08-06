"""
Insta485 users view.

URLs include: /users/<user_url_slug>/

"""

import flask
import insta485


@insta485.app.route('/users/<path:username>/', methods=['POST', 'GET'])
def show_user(username):
    """Display /users/username/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username FROM users"
    )

    user_list = []
    for user in cur.fetchall():
        user_list.append(user['username'])
    if username not in user_list:
        flask.abort(404)

    # ------------------------------------------------------------------------
    # Start making the context dict, which includes logname, username, posts,
    # logname_follows_username, fullname, following, followers, total_posts
    # ------------------------------------------------------------------------

    logname = flask.session.get('username')

    cur = connection.execute(
        "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )
    logname_follows_username = (len(cur.fetchall()) == 1)

    cur = connection.execute(
        "SELECT fullname FROM users WHERE username = ?",
        (username, )
    )
    fullname = cur.fetchall()[0]['fullname']

    cur = connection.execute(
        "SELECT count(1) AS following FROM following WHERE username1 = ?",
        (username, )
    )
    following = cur.fetchall()[0]['following']

    cur = connection.execute(
        "SELECT count(1) AS followers FROM following WHERE username2 = ?",
        (username, )
    )
    followers = cur.fetchall()[0]['followers']

    cur = connection.execute(
        "SELECT count(1) AS total_posts FROM posts WHERE owner = ?",
        (username, )
    )
    total_posts = cur.fetchall()[0]['total_posts']

    cur = connection.execute(
        "SELECT postid, filename FROM posts WHERE owner = ?",
        (username, )
    )
    posts = cur.fetchall()
    posts_detail = []
    for post in posts:
        posts_detail.append({
            'postid': post['postid'],
            'img_url': '/uploads/' + post['filename']
        })

    context = {
        'logname': logname,
        'username': username,
        'logname_follows_username': logname_follows_username,
        'fullname': fullname,
        'following': following,
        'followers': followers,
        'total_posts': total_posts,
        'posts': posts_detail
    }
    return flask.render_template("user.html", **context)
