import { apiConstants } from '../../constants/api.constants';

export function getApi(state = {}, action) {
  switch (action.type) {
    case apiConstants.GET_API_REQUEST:
      return { fetching : true };
    case apiConstants.GET_API_SUCCESS:
      return {...action.data};
    case apiConstants.GET_API_FAILURE:
      return {error: action.error};
    default:
      return state;
  }
}

export function postApi(state = {}, action) {
  switch (action.type) {
    case apiConstants.POST_API_REQUEST:
      return { fetching : true };
    case apiConstants.POST_API_SUCCESS:
      return {...action.res};
    case apiConstants.POST_API_FAILURE:
      return {error: action.error};
    default:
      return state;
  }
}

