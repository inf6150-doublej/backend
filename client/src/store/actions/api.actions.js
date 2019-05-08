import { apiConstants } from '../../constants/api.constants';

function handleResponse(response) {
    if (!response.ok) {
      return Promise.reject(response.statusText);
    }
    return response.json();
  }
  
  export function get(endpoint) {
    function request() { return { type: apiConstants.GET_API_REQUEST }; }
    function success(data) { return { type: apiConstants.GET_API_SUCCESS, data }; }
    function failure(error) { return { type: apiConstants.GET_API_FAILURE, error }; }
  
    return (dispatch) => {
      dispatch(request());
      fetch(endpoint, { credentials: 'include' })
        .then(handleResponse)
        .then((res) => {
          dispatch(success(res));
        })
        .catch((err) => {
          dispatch(failure(err));
        });
    };
  }

  export function post(endpoint, data) {
    function request() { return { type: apiConstants.POST_API_REQUEST }; }
    function success(data) { return { type: apiConstants.POST_API_SUCCESS, data }; }
    function failure(error) { return { type: apiConstants.POST_API_FAILURE, error }; }

    const requestOptions = {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    };
    
    return (dispatch) => {
      dispatch(request());
      fetch(endpoint, requestOptions)
        .then(handleResponse)
        .then((res) => {
          dispatch(success(res));
        })
        .catch((err) => {
          dispatch(failure(err));
        });
    };
  }