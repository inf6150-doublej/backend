import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import { get, post } from './store/actions/api.actions';
import logo from './img/logo.svg';
import './css/App.css';

class App extends Component {
  state = {
    response: '',
    data: '',
    responseToPost: '',
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(get('/salles/1'));
  }

  handleSubmit = e => {
    e.preventDefault();
    const { dispatch } = this.props;
    const user = { username : 'luce', password: 'ju' }
    dispatch(post('/login', {username : 'luce', password: 'ju'}));
  };

  render() {
    const { getApi, postApi } = this.props;
    console.log(getApi);
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.js</code> and save to reload.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>
        <p>{getApi.alo}</p>

        <form onSubmit={this.handleSubmit}>
          <p>
            <strong>Post to Server:</strong>
          </p>
          <input 
            type="text"
            value={this.state.data}
            onChange={e => this.setState({ data: e.target.value })}
          />
          <button type="submit">Submit</button>
        </form>

        <form onSubmit={this.handleSubmit}>
          <p>
            <strong>login</strong>
          </p>
          <input 
            type="text"
            value={this.state.data}
            onChange={e => this.setState({ data: e.target.value })}
          />
          <button type="submit">Submit</button>
        </form>
        <p>{postApi.data}</p>
      </div>
    );
  }
}

App.propTypes = {
  dispatch: PropTypes.func.isRequired,
  actions: PropTypes.object,
  fetchData: PropTypes.array,
  isFetching: PropTypes.bool,
  username: PropTypes.string,
};

function mapStateToProps(state) {
  const { getApi, postApi } = state;
  console.log(getApi)
  return {
    getApi,
    postApi,
  };
}

export default connect(mapStateToProps) (App);
