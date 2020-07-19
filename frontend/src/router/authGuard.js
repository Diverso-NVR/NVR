import store from "@/store";
import { isAdmin, isAdminOrEditor } from "@/utils";

export function adminOnly(to, from, next) {
  if (isAdmin()) {
    next();
  } else next("/");
}

export function adminOrEditor(to, from, next) {
  if (isAdminOrEditor()) {
    next();
  } else next("/");
}

export function authRequired(to, from, next) {
  if (!store.getters.isAutheticated) {
    next("/login");
  } else {
    next();
  }
}
