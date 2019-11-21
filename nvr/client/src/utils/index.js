export function isValidToken(token) {
  if (!token || token.split(".").length < 3) {
    return false;
  }

  const data = JSON.parse(atob(token.split(".")[1]));
  const exp = new Date(data.exp * 1000);
  const now = new Date();

  return now < exp;
}
