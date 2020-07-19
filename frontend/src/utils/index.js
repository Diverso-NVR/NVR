import store from "@/store";

export function isValidToken(token) {
  if (!token || token.split(".").length < 3) {
    return false;
  }

  const data = JSON.parse(atob(token.split(".")[1]));
  const exp = new Date(data.exp * 1000);
  const now = new Date();

  return now < exp;
}

export function isAdmin() {
  if (/^\w*admin$/.test(store.getters.user.role)) {
    return true;
  } else {
    return false;
  }
}

export function isAdminOrEditor() {
  if (
    /^\w*admin$/.test(store.getters.user.role) ||
    store.getters.user.role === "editor"
  ) {
    return true;
  } else {
    return false;
  }
}
