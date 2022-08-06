"""
Insta485 explore view.

URLs include: /explore/

"""

import flask
import insta485


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def show_explore():
    """Show the explore page."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    # Get the not_following dictionary needed for template
    logname = flask.session.get('username')
    cur = connection.execute(
        "SELECT username FROM users WHERE username != ? "
        "AND username not in (SELECT username2 FROM following "
        "WHERE username1 = ?)",
        (logname, logname)
    )
    unfollowing = cur.fetchall()
    unfollow_details = []
    # not_following consists of username and user_img_url
    for unfollow in unfollowing:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (unfollow['username'], )
        )
        filename = cur.fetchall()[0]['filename']
        unfollow_details.append({
            'username': unfollow['username'],
            'user_img_url': '/uploads/' + filename
            })

    context = {
        "logname": logname,
        "not_following": unfollow_details
    }
    return flask.render_template('explore.html', **context)
