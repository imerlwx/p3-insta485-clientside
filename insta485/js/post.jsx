import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import Comments from './comments';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
      */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      created: '',
      postid: 0,
      lognameLikesThis: false,
      numLikes: 0,
      likesUrl: '',
      comments: [],
    };
    // this.ismounted = false;
    // this.handleDoubleClick = this.handleDoubleClick.bind(this);
    // this.handleButtonChange = this.handleButtonChange.bind(this);
    this.unlikePost = this.unlikePost.bind(this);
    this.likePost = this.likePost.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    // , lognameLikesThis, numLikes, likesUrl,
    // this.setState({
    //   lognameLikesThis: lognameLikesThis,
    //   numLikes: numLikes,
    //   likesUrl: likesUrl,
    // });
    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // this.ismounted = true;
        this.setState({
          imgUrl: data.imgUrl,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postShowUrl: data.postShowUrl,
          created: data.created,
          postid: data.postid,
          lognameLikesThis: data.likes.lognameLikesThis,
          numLikes: data.likes.numLikes,
          likesUrl: data.likes.url,
          comments: data.comments,
        });
      })
      .catch((error) => console.log(error));
  }

  // componentWillUnmount() {
  //   this.ismounted = false;
  // }

  // handleDoubleClick(event) {
  //   // This function will handle the double click on the image
  //   event.preventDefault();
  //   const { postid, lognameLikesThis, numLikes } = this.state;
  //   const postUrl = `/api/v1/likes/?postid=${postid}`;
  //   console.log();

  //   if (!lognameLikesThis) {
  //     fetch(postUrl, { credentials: 'same-origin', method: 'POST' })
  //       .then((response) => {
  //         if (!response.ok) throw Error(response.statusText);
  //         return response.json();
  //       })
  //       .then((data) => {
  //         this.setState({
  //           lognameLikesThis: true,
  //           numLikes: numLikes + 1,
  //           likesUrl: data.url,
  //         });
  //       })
  //       .catch((error) => console.log(error));
  //   }
  // }

  unlikePost(event, oneLikeUrl) {
    event.preventDefault();
    const { numLikes } = this.state;
    fetch(oneLikeUrl, { credentials: 'same-origin', method: 'DELETE' })
      .then(() => {
        this.setState({
          lognameLikesThis: false,
          numLikes: numLikes - 1,
          likesUrl: null,
        });
      });
  }

  likePost(event) {
    // This function will handle the state change of pressing the like/unlike button
    event.preventDefault();
    const { postid, numLikes } = this.state;
    const postUrl = `/api/v1/likes/?postid=${postid}`;
    console.log(postid);

    fetch(postUrl, { credentials: 'same-origin', method: 'POST' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          lognameLikesThis: true,
          numLikes: numLikes + 1,
          likesUrl: data.url,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns some values in this.state to the const variables
    window.onpopstate = () => {
      window.history.back();
    };
    const {
      imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, created,
      postid, lognameLikesThis, numLikes, likesUrl, comments,
    } = this.state;
    const ownerNameStyle = { position: 'absolute', top: '15px', left: '50px' };
    const timestampStyle = { float: 'right', padding: '30px 15px' };

    function clickEvent(event, lognameLikes, likePost) {
      event.preventDefault();
      if (!lognameLikes) {
        likePost(event);
      }
    }

    // Render number of post image and post owner
    return (
      <div className="post">
        <div className="hyperlinkstyle">
          <a href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="description for user" width="40" style={{ postion: 'absolute' }} />
          </a>
          <a href={ownerShowUrl} style={ownerNameStyle}>{owner}</a>
          <a href={postShowUrl} style={timestampStyle}>{moment.utc(created, 'YYYY-MM-DD hh:mm:ss').fromNow()}</a>
        </div>
        <br />
        <br />
        <br />
        <img src={imgUrl} alt="description of post" onDoubleClick={(event) => clickEvent(event, lognameLikesThis, this.likePost)} />
        <ShowLikeButton
          lognameLikesThis={lognameLikesThis}
          unlikePost={this.unlikePost}
          likePost={this.likePost}
          oneLikeUrl={likesUrl}
        />
        <br />
        <Like numLikes={numLikes} />
        <Comments comments={comments} postid={postid} />
      </div>
    );
  }
}

function Like(props) {
  const { numLikes } = props;
  let likeGrammar;
  if (numLikes === 1) {
    likeGrammar = 'like';
  } else {
    likeGrammar = 'likes';
  }
  return (
    <p style={{ marginLeft: '1.5pem' }}>
      {`${numLikes} ${likeGrammar}`}
    </p>
  );
}

function ShowLikeButton(props) {
  const {
    lognameLikesThis, unlikePost, likePost, oneLikeUrl,
  } = props;
  if (lognameLikesThis) {
    return (
      <button type="button" className="like-unlike-button" onClick={(event) => unlikePost(event, oneLikeUrl)} style={{ marginLeft: '1.5rem' }}>
        Unlike
      </button>
    );
  }
  return (
    <button type="button" className="like-unlike-button" onClick={(event) => likePost(event)} style={{ marginLeft: '1.5rem' }}>
      Like
    </button>
  );
}

Like.propTypes = {
  numLikes: PropTypes.number.isRequired,
};

ShowLikeButton.propTypes = {
  lognameLikesThis: PropTypes.bool.isRequired,
  unlikePost: PropTypes.func.isRequired,
  likePost: PropTypes.func.isRequired,
  oneLikeUrl: PropTypes.string,
};

ShowLikeButton.defaultProps = {
  oneLikeUrl: 'null',
};

Post.propTypes = {
  url: PropTypes.string.isRequired,
  // lognameLikesThis: PropTypes.bool.isRequired,
  // numLikes: PropTypes.number.isRequired,
  // likesUrl: PropTypes.string,
};

export default Post;
