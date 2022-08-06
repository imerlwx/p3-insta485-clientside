"""
Insta485 followers view.

URLs include: /users/<user_url_slug>/followers/

"""

import flask
import insta485
from insta485.views.follow import follow_unfollow_request


@insta485.app.route('/users/<path:username>/followers/',
                    methods=['POST', 'GET'])
def show_followers(username):
    """Display /users/username/followers route."""
    # -----------------------------------------------------------------------
    # Start making the context dictionary, which includes logname, followers
    # followers includes username, user_img_url, logname_follows_username
    # -----------------------------------------------------------------------
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username "
        "FROM users")
    userslist = []
    for user in cur.fetchall():
        userslist.append(user['username'])
    if username not in userslist:
        flask.abort(404)

    logname = flask.session.get('username')
    if flask.request.method == 'POST':
        follow_unfollow_request()

    cur = connection.execute(
        "SELECT u.username, u.filename FROM users u JOIN following f "
        "ON u.username = f.username1 WHERE f.username2 = ?",
        (username, )
    )
    followers = cur.fetchall()
    followers_detail = []
    for follower in followers:
        follower_username = follower['username']
        follower_user_img_url = '/uploads/' + follower['filename']
        cur = connection.execute(
            "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
            (logname, follower_username, )
        )
        logname_follows_username = (len(cur.fetchall()) == 1)
        followers_detail.append({
            'username': follower_username,
            'user_img_url': follower_user_img_url,
            'logname_follows_username': logname_follows_username
        })

    context = {
        'logname': logname,
        'username': username,
        'followers': followers_detail
    }
    return flask.render_template('followers.html', **context)
