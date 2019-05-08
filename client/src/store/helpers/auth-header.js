
export function authHeader() {
  // return authorization header with jwt token
  const user = JSON.parse(localStorage.getItem('user'));

  if (user && user.id_token) {
    return { Authorization: `Bearer ${user.id_token}` };
  }
  return {};
}

