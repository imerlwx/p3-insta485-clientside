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
      allPosts: [],
      results: [],
      next: '',
      allLength: 0,
      hasMore: true,
    };
    this.handleScroll = this.handleScroll.bind(this);
  }

  componentDidMount() {
    // Handle the browser history navigation
    performance.mark('Begin');
    window.onpopstate = () => {
      window.history.back();
    };
    performance.mark('End');

    // This line automatically assigns this.props.url to the const variable url
    setTimeout(() => {
      const { url } = this.props;
      this.setState({
        next: url,
        hasMore: true,
      });
      // Call REST API to get the post's information
      fetch(url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          // this.ismounted = true;
          this.setState({
            results: data.results,
            next: data.next,
          });
          const { results } = this.state;
          const { allPosts } = this.state;
          results.forEach((post) => {
            allPosts.push(
              <Post url={post.url} key={post.postid} />,
            );
          });

          this.setState((prevState) => ({
            allLength: prevState.allLength + results.length,
          }));
          this.setState({ hasMore: true });
        })
        .catch((error) => console.log(error));
    }, 500);
  }

  handleScroll() {
    performance.mark('Begin');
    performance.mark('End');
    const { allPosts, next } = this.state;
    if (next !== '') {
      fetch(next, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            results: data.results,
            next: data.next,
          });

          const { results } = this.state;
          results.forEach((post) => {
            allPosts.push(
              <Post url={post.url} key={post.postid} />,
            );
          });
          this.setState((prevState) => ({
            allLength: prevState.allLength + results.length,
          }));
          this.setState({ hasMore: true });
        })
        .catch((error) => console.log(error));
    } else {
      this.setState({ hasMore: false });
    }
  }

  render() {
    // Use the history API to manipulate browser history.
    // Use PerformanceNavigationTiming API to check how the user
    // is navigating to and from a page.
    // if (String(window.performance.getEntriesByType('navigation')[0].type) === 'back_forward') {
    //   this.state = window.history.state;
    // }
    // window.history.replaceState(this.state, '', '/');
    const { allPosts, allLength, hasMore } = this.state;
    return (
      <InfiniteScroll
        dataLength={allLength}
        next={this.handleScroll}
        hasMore={hasMore}
        loader={<h4>Loading...</h4>}
      >
        <div className="posts">
          {allPosts}
        </div>
      </InfiniteScroll>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
