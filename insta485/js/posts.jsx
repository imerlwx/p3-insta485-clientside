import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Posts extends React.Component {
  /* Display number of image and post owner of a single post
      */
  constructor(props) {
    super(props);
    this.state = {
      postsInfo: [],
      next: '',
    };
    this.handleScroll = this.handleScroll.bind(this);
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
          postsInfo: data.results,
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  handleScroll() {
    const { postsInfo, next } = this.state;
    fetch(next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // this.ismounted = true;
        this.setState({
          postsInfo: postsInfo.concat(data.results),
          next: data.next,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // Use the history API to manipulate browser history.
    // Use PerformanceNavigationTiming API to check how the user
    // is navigating to and from a page.
    if (String(window.performance.getEntriesByType('navigation')[0].type) === 'back_forward') {
      this.state = window.history.state;
    }
    const { postsInfo, next } = this.state;
    return (
      <div className="posts">
        <InfiniteScroll
          dataLength={postsInfo.length}
          next={this.handleScroll}
          hasMore={next !== ''}
          loader={<h4>Loading...</h4>}
        >
          {postsInfo.map((post) => (
            <div key={post.postid}>
              <Post url={post.url} />
            </div>
          ))}
        </InfiniteScroll>
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
