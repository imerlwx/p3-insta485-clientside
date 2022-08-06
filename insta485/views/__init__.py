"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.user import show_user
from insta485.views.likes import like_unlike_request
from insta485.views.comment import comments_request
from insta485.views.post_op import create_delete_posts

from insta485.views.accounts import accounts_operation
from insta485.views.accounts import login
from insta485.views.accounts import logout
from insta485.views.accounts import create
from insta485.views.accounts import delete
from insta485.views.accounts import edit
from insta485.views.accounts import password_

from insta485.views.follow import follow_unfollow_request
from insta485.views.following import show_following
from insta485.views.followers import show_followers
from insta485.views.explore import show_explore
from insta485.views.post import show_post
