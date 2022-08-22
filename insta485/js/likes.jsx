import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
  /* Control the like component of the post and posts component
      */
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(event) {
    const { onLognameLikesChange } = this.props;
    event.preventDefault();
    onLognameLikesChange();
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { lognameLikesThis, numLikes } = this.props;
    // Render number of post image and post owner
    return (
      <div>
        <button type="button" className="like-unlike-button" onClick={this.handleClick}>
          {lognameLikesThis ? 'unlike' : 'like'}
        </button>
        <p>
          <span>{numLikes}</span>
          <span>{numLikes === 1 ? 'like' : 'likes'}</span>
        </p>
      </div>
    );
  }
}

Likes.propTypes = {
  onLognameLikesChange: PropTypes.func.isRequired,
  lognameLikesThis: PropTypes.bool.isRequired,
  numLikes: PropTypes.number.isRequired,
};

export default Likes;
