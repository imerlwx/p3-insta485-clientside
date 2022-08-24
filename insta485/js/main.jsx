import React from 'react';
import ReactDOM from 'react-dom';
import Posts from './posts';

// This method is only called once
ReactDOM.render(
  // Insert the post component into the DOM
  <Posts url="/api/v1/posts/" />,
  document.getElementById('reactEntry'),
);
