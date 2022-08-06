"""
Insta485 following view.

URLs include: /users/<user_url_slug>/following/

"""

import flask
import insta485
from insta485.views.follow import follow_unfollow_request


@insta485.app.route('/users/<path:username>/following/',
                    methods=['POST', 'GET'])
def show_following(username):
    """Display /users/username/following route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()

    userlist = []
    cur = connection.execute(
        "SELECT username "
        "FROM users")

    for user in cur.fetchall():
        userlist.append(user['username'])
    if username not in userlist:
        flask.abort(404)

    if flask.request.method == 'POST':
        follow_unfollow_request()

    # ------------------------------------------------------------------------
    # Start making the context dictionary, which includes logname, following
    # The following includes username, user_img_url, logname_follows_username
    # ------------------------------------------------------------------------

    logname = flask.session.get('username')

    cur = connection.execute(
        "SELECT u.username, u.filename FROM users u JOIN following f "
        "ON u.username = f.username2 WHERE f.username1 = ?",
        (username, )
    )
    followings = cur.fetchall()
    following_detail = []
    for following in followings:
        following_username = following['username']
        following_user_img_url = '/uploads/' + following['filename']
        cur = connection.execute(
            "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
            (logname, following_username, )
        )
        logname_follows_username = (len(cur.fetchall()) == 1)
        following_detail.append({
            'username': following_username,
            'user_img_url': following_user_img_url,
            'logname_follows_username': logname_follows_username
        })

    context = {
        'logname': logname,
        'username': username,
        'following': following_detail
    }
    return flask.render_template('following.html', **context)
