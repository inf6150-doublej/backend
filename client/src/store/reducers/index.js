import { combineReducers } from 'redux';
import { authentication } from './authentication.reducer';
import { registration } from './registration.reducer';
import { users } from './users.reducer';
import { getApi, postApi } from './api.reducer'


const rootReducer = combineReducers({
  authentication,
  registration,
  users,
  getApi,
  postApi
});

export default rootReducer;
