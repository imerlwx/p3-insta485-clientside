import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  /* Control the comments component of the post and posts component
      */
  constructor(props) {
    super(props);
    this.state = { comments: [], value: '' };
    this.handleChange = this.handleChange.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  static getDerivedStateFromProps(props, state) {
    const prevProps = state.prevProps || {};
    const controlledValue = prevProps.comments !== props.comments ? props.comments : state.comments;
    return {
      prevProps: props,
      comments: controlledValue,
    };
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleKeyDown(event) {
    // This function will handle the new created comment
    const { postid } = this.props;
    const url = `/api/v1/comments/?postid=${postid}`;
    event.preventDefault();
    const { value } = this.state;
    console.log(value);
    const requestOptions = {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: value }),
    };
    fetch(url, requestOptions)
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          comments: prevState.comments.concat(data),
          value: '',
        })); // Use prevState to update the comments database
      })
      .catch((error) => console.log(error));
  }

  handleClick(commentid, url) {
    // This function will handle the click on the delete comment button
    fetch(url, { credentials: 'same-origin', method: 'DELETE' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then(() => {
        this.setState((prevState) => ({
          comments: prevState.comments.filter((comment) => comment.commentid !== commentid),
        })); // Use .filter to filter out the comment with commentid
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { value, comments } = this.state;
    const ownerStyle = {
      float: 'left', lineHeight: '5px', marginTop: '-10px', fontWeight: 'bold',
    };
    const buttonStyle = { float: 'right', marginRight: '5px' };

    return (
      <div>
        {comments.map((comment) => (
          <p key={comment.commentid}>
            <a href={comment.ownerShowUrl} style={ownerStyle}>{comment.owner}</a>
            {comment.text}
            {comment.lognameOwnsThis ? (
              <button type="button" className="delete-comment-button" style={buttonStyle} onClick={this.handleClick.bind(this, comment.commentid, comment.url)}>
                Delete
              </button>
            ) : null}
          </p>
        ))}
        <form className="comment-form" onSubmit={this.handleKeyDown}>
          <input type="text" value={value} onChange={this.handleChange} />
        </form>
      </div>
    );
  }
}

Comments.propTypes = {
  postid: PropTypes.number.isRequired,
  comments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
      owner: PropTypes.string.isRequired,
      ownerShowUrl: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
    }),
  ).isRequired,
};
// å
export default Comments;
