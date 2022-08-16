"""REST API for posts."""
import flask
import insta485
from insta485.api.util import error_checking, wrong_password, invalid_postid


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    """Return post on postid_url_slug."""
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
    if invalid_postid(postid_url_slug):
        return flask.jsonify(**error_checking(404)), 404

    context = get_post_info(username, postid_url_slug)
    context["url"] = flask.request.path
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_posts():
    """Returns posts based on size, page and postid_lte."""
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

    # Request a specific number of results with ?size=N
    # Request a specific page of results with ?page=
    size = flask.request.args.get('size', default=10, type=int)
    page = flask.request.args.get('page', default=0, type=int)
    # Both size and page must be non-negative integers
    if size < 0 or page < 0:
        return flask.jsonify(**error_checking(400)), 400

    connection = insta485.model.get_db()
    postid_latest = connection.execute(
        "SELECT postid FROM posts ORDER BY postid DESC LIMIT 1"
    ).fetchall()[0]['postid']
    postid_lte = flask.request.args.get('postid_lte',
                                        default=postid_latest,
                                        type=int)

    # Get all the postids that meet the criteria
    cur = connection.execute(
        "SELECT postid FROM posts WHERE postid <= ? AND owner = ?"
        "OR postid <= ? AND owner IN"
        "(SELECT username2 FROM following WHERE username1 = ?)"
        "ORDER BY postid DESC LIMIT ? OFFSET ?",
        (postid_lte, username, postid_lte, username, size, size * page)
    )
    posts = cur.fetchall()

    # Build the json context, including the "next", "results" and "url"
    context = {}
    post_list = []
    for post in posts:
        post_info = {}
        post_info['postid'] = int(post['postid'])
        post_info['url'] = "/api/v1/posts/" + str(post['postid']) + "/"
        post_list.append(post_info)

    context["results"] = post_list
    if ("size" in flask.request.args or "page" in flask.request.args or
        "postid_lte" in flask.request.args):
        context["url"] = flask.request.full_path
    else:
        context["url"] = flask.request.path

    # Check if there is any next page
    posts_all = connection.execute(
        "SELECT postid FROM posts WHERE postid <= ? AND owner = ?"
        "OR postid <= ? AND owner IN"
        "(SELECT username2 FROM following WHERE username1 = ?)"
        "ORDER BY postid DESC",
        (postid_lte, username, postid_lte, username)
    ).fetchall()

    if len(posts_all) >= size * (page + 1):
        context["next"] = flask.request.path + "?size=" + str(size) + \
            "&page=" + str(page + 1) + "&postid_lte=" + str(postid_lte)
    else:
        context["next"] = ""

    return flask.jsonify(**context)


def get_post_info(username, postid_url_slug):
    """Get post details information."""
    connection = insta485.model.get_db()

    # Post details include the comments, created, imgUrl, likes, postid,
    # url, owner, ownerImgUrl, ownerShowUrl, postShowUrl
    cur = connection.execute(
        "SELECT filename AS imgUrl, owner, created "
        "FROM posts WHERE postid = ?", (postid_url_slug, )
    )
    info = cur.fetchall()[0]  # Contains imgUrl, owner, created

    # Make up likes dict
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
        (username, postid_url_slug, )
    )
    likeid = cur.fetchall()[0]['likeid']
    like_url = None
    lognameLikesThis = False
    if likeid is not None:
        like_url = "/api/v1/likes/" + str(likeid) + "/"
        lognameLikesThis = True

    cur = connection.execute(
        "SELECT count(likeid) AS numLikes FROM likes WHERE postid = ?",
        (postid_url_slug, )
    )

    likes = {
        "lognameLikesThis": lognameLikesThis,
        "numLikes": cur.fetchall()[0]['numLikes'],
        "url": like_url,
    }

    # Make up comments dict
    cur = connection.execute(
        "SELECT commentid FROM comments WHERE postid = ?", (postid_url_slug, )
    )
    commentid_list = []
    for commentid in cur.fetchall():
        commentid_list.append(commentid['commentid'])

    comments = []
    for commentid in commentid_list:
        cur = connection.execute(
            "SELECT owner, text FROM comments WHERE commentid = ?",
            (commentid, )
        )
        comment_info = cur.fetchall()[0]
        comments.append({
            "commentid": commentid,
            "lognameOwnsThis": comment_info['owner'] == username,
            "owner": comment_info['owner'],
            "ownerShowUrl": "/users/" + str(comment_info['owner']) + "/",
            "text": comment_info['text'],
            "url": "/api/v1/comments/" + str(commentid) + "/",
        })

    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ?", (info['owner'], )
    )

    context = {
        "comments": comments,
        "created": info['created'],
        "imgUrl": "/uploads/" + info['imgUrl'],
        "likes": likes,
        "owner": info['owner'],
        "ownerImgUrl": "/uploads/" + cur.fetchall()[0]['filename'],
        "ownerShowUrl": "/users/" + info['owner'] + "/",
        "postShowUrl": "/posts/" + str(postid_url_slug) + "/",
        "postid": postid_url_slug,
    }

    return context
