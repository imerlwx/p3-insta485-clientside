"""
Insta485 followers view.

URLs include: /posts/<postid_url_slug>/

"""

import arrow
import flask
import insta485
from insta485.views.post_op import create_delete_posts


@insta485.app.route('/posts/<path:postid>/', methods=['POST', 'GET'])
def show_post(postid):
    """Display the /posts/postid/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    if flask.request.method == 'POST':
        return create_delete_posts()

    # ------------------------------------------------------------------------
    # Making the context dict, which includes logname, postid, img_url, owner,
    # owner_img_url, timestamp, likes, comments (owner, text), like_or_not
    # ------------------------------------------------------------------------

    logname = flask.session.get('username')
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT filename AS img_url, owner, created AS timestamp "
        "FROM posts WHERE postid = ?",
        (postid, )
    )
    info = cur.fetchall()[0]
    owner = info['owner']
    img_url = '/uploads/' + info['img_url']
    timestamp = arrow.get(info['timestamp']).humanize()

    cur = connection.execute(
        "SELECT filename AS owner_img_url FROM users WHERE username = ?",
        (owner, )
    )
    owner_img_url = '/uploads/' + cur.fetchall()[0]['owner_img_url']

    cur = connection.execute(
        "SELECT count(1) AS likes_count FROM likes WHERE postid = ?",
        (postid, )
    )
    likes = cur.fetchall()[0]['likes_count']

    cur = connection.execute(
        "SELECT commentid, owner, text FROM comments WHERE postid = ?",
        (postid, )
    )
    comments = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid, )
    )
    like_or_not = (len(cur.fetchall()) == 1)

    context = {
        'logname': logname,
        'postid': postid,
        'owner': owner,
        'owner_img_url': owner_img_url,
        'img_url': img_url,
        'timestamp': timestamp,
        'likes': likes,
        'comments': comments,
        'like_or_not': like_or_not
    }

    return flask.render_template('post.html', **context)
