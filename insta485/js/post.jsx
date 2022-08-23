import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import Likes from './likes';
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
      postid: '',
      lognameLikesThis: '',
      numLikes: '',
      url: '',
      comments: [],
    };
    // this.ismounted = false;
    this.handleDoubleClick = this.handleDoubleClick.bind(this);
    this.handleButtonChange = this.handleButtonChange.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
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
          url: data.likes.url,
          comments: data.comments,
        });
      })
      .catch((error) => console.log(error));
  }

  // componentWillUnmount() {
  //   this.ismounted = false;
  // }

  handleDoubleClick() {
    // This function will handle the double click on the image
    const { postid, lognameLikesThis } = this.state;
    const postUrl = `/api/v1/likes/?postid=${postid}`;
    console.log();

    if (!lognameLikesThis) {
      fetch(postUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState((prevState) => ({
            lognameLikesThis: true,
            numLikes: prevState.numLikes + 1,
            url: data.url,
          }));
        })
        .catch((error) => console.log(error));
    }
  }

  handleButtonChange() {
    // This function will handle the state change of pressing the like/unlike button
    const { postid, lognameLikesThis, url } = this.state;
    const postUrl = `/api/v1/likes/?postid=${postid}`;

    if (lognameLikesThis) {
      fetch(url, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then(() => {
          this.setState((prevState) => ({
            lognameLikesThis: false,
            numLikes: prevState.numLikes - 1,
            url: postUrl,
          }));
        })
        .catch((error) => console.log(error));
    } else {
      fetch(postUrl, { credentials: 'same-origin', method: 'POST' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState((prevState) => ({
            lognameLikesThis: true,
            numLikes: prevState.numLikes + 1,
            url: data.url,
          }));
        })
        .catch((error) => console.log(error));
    }
  }

  render() {
    // This line automatically assigns some values in this.state to the const variables
    const {
      imgUrl, owner, ownerImgUrl, ownerShowUrl, postShowUrl, created,
      postid, lognameLikesThis, numLikes, url, comments,
    } = this.state;
    const ownerNameStyle = { padding: '30px 0px' };
    const timestampStyle = { padding: '30px 15px', float: 'right' };
    // Render number of post image and post owner
    return (
      <div className="post">
        <div>
          <a href={ownerShowUrl}>
            <img className="propic" src={ownerImgUrl} alt="" />
          </a>
          <a href={ownerShowUrl} style={ownerNameStyle}>{owner}</a>
          <a href={postShowUrl} style={timestampStyle}>{moment.utc(created, 'YYYY-MM-DD hh:mm:ss').fromNow()}</a>
        </div>
        <img src={imgUrl} alt="" onDoubleClick={this.handleDoubleClick} />
        <Likes
          lognameLikesThis={lognameLikesThis}
          numLikes={numLikes}
          url={url}
          onLognameLikesChange={this.handleButtonChange}
          postid={postid}
        />
        <Comments comments={comments} postid={postid} />
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
