import store from "@/store";

export function adminOnly(to, from, next) {
  if (store.getters.user.role === "admin") {
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
