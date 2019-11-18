import store from "@/store";

export function adminOnly(to, from, next) {
  if (/^\w*admin$/.test(store.getters.user.role)) {
    next();
  } else next("/login");
}

export function authRequired(to, from, next) {
  if (!store.getters.isAutheticated) {
    next("/login");
  } else {
    next();
  }
}
