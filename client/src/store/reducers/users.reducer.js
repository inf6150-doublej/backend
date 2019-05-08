import { userConstants } from '../../constants';

const { GETALL_FAILURE, GETALL_REQUEST, GETALL_SUCCESS, DELETE_FAILURE, DELETE_REQUEST, DELETE_SUCCESS, SESSION_FAILURE, SESSION_SUCCESS, SESSION_REQUEST } = userConstants;

function users(state = {}, action) {
  switch (action.type) {
    case GETALL_REQUEST:
      return {
        loading: true,
      };
    case GETALL_SUCCESS:
      return {
        users: action.users,
      };
    case GETALL_FAILURE:
      return {
        error: action.error,
      };
    case DELETE_REQUEST:
      // add 'deleting:true' property to user being deleted
      return {
        ...state,
        users: state.users.map(user => user.id === action.id ? { ...user, deleted: true } : user),
      };
    case DELETE_SUCCESS:
      // remove deleted user from state
      return {
        users: state.users.filter(user => user.id !== action.id),
      };
    case DELETE_FAILURE:
      // remove 'deleting:true' property and add 'deleteError:[error]' property to user
      return {
        ...state,
        users: state.users.map((user) => {
          if (user.id === action.id) {
            // make copy of user without 'deleting:true' property
            const { deleted, ...userCopy } = user;
            // return copy of user with 'deleteError:[error]' property
            return { ...userCopy, deleteError: action.error };
          }
          return user;
        }),
      };
    default:
      return state;
  }
}


export { users };
