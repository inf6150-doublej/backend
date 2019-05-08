// import cookie from 'react-cookie';
import { authHeader } from './auth-header';
import { urlConstants } from '../../constants';

function handleResponse(response) {
  if (!response.ok) {
    return Promise.reject(response.statusText);
  }
  return response.json();
}

function login(username, password) {
  const { LOGIN_URL } = urlConstants;
  const requestOptions = {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  };

  return fetch(LOGIN_URL, requestOptions)
    .then(handleResponse)
    .then(res => res);
}

function logout() {
  // cookie.remove('session');
  localStorage.removeItem('user');
}

function getAll() {
  const requestOptions = {
    method: 'GET',
    headers: authHeader(),
  };
  return fetch('/users', requestOptions).then(handleResponse);
}

function getById(id) {
  const requestOptions = {
    method: 'GET',
    headers: authHeader(),
  };
  return fetch(`${'/users/'}${id}`, requestOptions).then(handleResponse);
}

function register(user) {
  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  };
  return fetch(urlConstants.REGISTER_URL, requestOptions).then(handleResponse);
}

function update(user) {
  const requestOptions = {
    method: 'PUT',
    headers: { ...authHeader(), 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  };
  return fetch(`${'/users/'}user.id`, requestOptions).then(handleResponse);
}

// prefixed function name with underscore because delete is a reserved word in javascript
function deleteUser(id) {
  const requestOptions = {
    method: 'DELETE',
    headers: authHeader(),
  };

  return fetch(`${'/users/'}${id}`, requestOptions).then(handleResponse);
}

export const userServices = {
  login,
  logout,
  register,
  getAll,
  getById,
  update,
  deleteUser,
};
