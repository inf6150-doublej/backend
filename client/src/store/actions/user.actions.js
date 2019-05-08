import cookie from 'react-cookie';
import { userConstants, urlConstants } from '../../constants';

const { HOME_URL } = urlConstants;

function handleResponse(response) {
  if (!response.ok) {
    return Promise.reject(response.statusText);
  }
  return response.json();
}

export function checkSession() {
  function request() { return { type: userConstants.SESSION_REQUEST }; }
  function success(user) { return { type: userConstants.SESSION_SUCCESS, user }; }
  function failure(err) { return { type: userConstants.SESSION_FAILURE, err }; }

  return (dispatch) => {
    dispatch(request());
    fetch(HOME_URL, { credentials: 'include' })
      .then(handleResponse)
      .then((user) => {dispatch(success(user));})
      .catch((err) => {dispatch(failure(err));});
  };
}

function login(username, password) {
  function request(user) { return { type: userConstants.LOGIN_REQUEST, user }; }
  function success(user) { return { type: userConstants.LOGIN_SUCCESS, user }; }
  function failure(err) { return { type: userConstants.LOGIN_FAILURE, err }; }

  return (dispatch) => {
    dispatch(request({ username }));
    const { LOGIN_URL } = urlConstants;
    const requestOptions = {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    };
  
    fetch(LOGIN_URL, requestOptions)
      .then(handleResponse)
      .then((user) => {
                // TODO add history push myaccount
        dispatch(success(user));
      })
      .catch((err) => {dispatch(failure(err));});
  };
}

export function logout() {
  cookie.remove('session');
  return { type: userConstants.LOGOUT };
}

function register(user) {
  function request(user) { return { type: userConstants.REGISTER_REQUEST, user }; }
  function success(user) { return { type: userConstants.REGISTER_SUCCESS, user }; }
  function failure(err) { return { type: userConstants.REGISTER_FAILURE, err }; }

  return (dispatch) => {
    dispatch(request(user));
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user),
    };
    fetch(urlConstants.REGISTER_URL, requestOptions)
      .then(handleResponse)
      .then((user)=>dispatch(success(user)))
      .catch((err)=>dispatch(failure(err)))
  };
}

function updateUser(user) {
  const { UPDATE_USER_REQUEST, UPDATE_USER_SUCCESS, UPDATE_USER_FAILURE } = userConstants;
  const { UPDATE_USER_URL } = urlConstants;
  const url = `${UPDATE_USER_URL}${user.id}`;
  const requestOptions = {
    method: 'UPDATE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user }),
  };

  function request() { return { type: UPDATE_USER_REQUEST }; }
  function success(_user) { return { type: UPDATE_USER_SUCCESS, _user }; }
  function failure(err) { return { type: UPDATE_USER_FAILURE, err }; }

  return (dispatch) => {
    dispatch(request());
    fetch(url, requestOptions)
      .then(handleResponse)
      .then((user) => {dispatch(success(user));})
      .catch((err) => {dispatch(failure(err));});
  };
}


function deleteUser(id) {
  function request(id) { return { type: userConstants.DELETE_REQUEST, id }; }
  function success(id) { return { type: userConstants.DELETE_SUCCESS, id }; }
  function failure(id, err) { return { type: userConstants.DELETE_FAILURE, id, err }; }

  return (dispatch) => {
    dispatch(request(id));

    const requestOptions = {method: 'DELETE'};
    fetch(`${'/users/'}${id}`, requestOptions)
      .then(handleResponse)
      .then((id)=>{dispatch(success(id))})
      .catch((err)=>{dispatch(failure(id, err))})
  }
}

export const userActions = {
  login,
  logout,
  register,
  delete: deleteUser,
  checkSession,
  updateUser,
};
