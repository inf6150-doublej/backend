import { userConstants, urlConstants } from '../../constants';
import { userServices }  from '../helpers';

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
  function failure(error) { return { type: userConstants.SESSION_FAILURE, error }; }

  return (dispatch) => {
    dispatch(request());
    fetch(HOME_URL, { credentials: 'include' })
      .then(handleResponse)
      .then((user) => {
        dispatch(success(user));
      })
      .catch((err) => {
        dispatch(failure(err));
      });
  };
}

function login(username, password) {
  function request(user) { return { type: userConstants.LOGIN_REQUEST, user }; }
  function success(user) { return { type: userConstants.LOGIN_SUCCESS, user }; }
  function failure(error) { return { type: userConstants.LOGIN_FAILURE, error }; }

  return (dispatch) => {
    dispatch(request({ username }));
    userServices.login(username, password)
      .then((user) => {
        dispatch(success(user));
        // TODO add history push myaccount
      })
      .catch((error) => {
        dispatch(failure(error));
      });
  };
}

export function logout() {
  userServices.logout();
  return { type: userConstants.LOGOUT };
}

function register(user) {
  function request(user) { return { type: userConstants.REGISTER_REQUEST, user }; }
  function success(user) { return { type: userConstants.REGISTER_SUCCESS, user }; }
  function failure(error) { return { type: userConstants.REGISTER_FAILURE, error }; }

  return (dispatch) => {
    dispatch(request(user));
    userServices.register(user)
      .then(
        () => {
          dispatch(success());
          // TODO add history push home
        },
        (error) => {
          dispatch(failure(error));
        },
      );
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
  function failure(error) { return { type: UPDATE_USER_FAILURE, error }; }

  return (dispatch) => {
    dispatch(request());
    fetch(url, requestOptions)
      .then((res) => {
        console.log('res :', res);
        dispatch(success(res));
      })
      .catch((err) => {
        dispatch(failure(err));
      });
  };
}

function getAll() {
  function request() { return { type: userConstants.GETALL_REQUEST }; }
  function success(users) { return { type: userConstants.GETALL_SUCCESS, users }; }
  function failure(error) { return { type: userConstants.GETALL_FAILURE, error }; }

  return (dispatch) => {
    dispatch(request());
    userServices.getAll()
      .then(
        users => dispatch(success(users)),
        error => dispatch(failure(error)),
      );
  };
}

function deleteUser(id) {
  function request(id) { return { type: userConstants.DELETE_REQUEST, id }; }
  function success(id) { return { type: userConstants.DELETE_SUCCESS, id }; }
  function failure(id, error) { return { type: userConstants.DELETE_FAILURE, id, error }; }

  return (dispatch) => {
    dispatch(request(id));
    userServices.delete(id)
      .then(
        () => {
          dispatch(success(id));
        },
        (error) => {
          dispatch(failure(id, error));
        },
      );
  };
}

export const userActions = {
  login,
  logout,
  register,
  getAll,
  delete: deleteUser,
  checkSession,
  updateUser,
};
