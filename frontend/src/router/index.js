import Vue from "vue";
import Router from "vue-router";
import { adminOnly, adminOrEditor, authRequired } from "./authGuard";

Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: "/",
      redirect: "/rooms"
    },
    {
      path: "/login",
      component: () => import("@/components/auth/Login"),
      meta: { title: "Вход" }
    },
    {
      path: "/register",
      component: () => import("@/components/auth/Register"),
      meta: { title: "Регистрация" }
    },
    {
      path: "/reset-pass",
      component: () => import("@/components/auth/GetEmail"),
      meta: { title: "Сброс пароля" }
    },
    {
      path: "/reset-pass/:token",
      component: () => import("@/components/auth/ResetPass"),
      meta: { title: "Сброс пароля" }
    },
    {
      path: "/rooms",
      component: () => import("@/components/campus/Rooms"),
      beforeEnter: authRequired,
      meta: { title: "Аудитории" }
    },
    {
      path: "/records",
      component: () => import("@/components/users/Records"),
      beforeEnter: authRequired,
      meta: { title: "Записи" }
    },
    {
      path: "/streaming",
      component: () => import("@/components/campus/Streaming"),
      beforeEnter: authRequired,
      meta: { title: "Стриминг" }
    },
    {
      path: "/access-requests",
      component: () => import("@/components/users/AccessRequests"),
      beforeEnter: adminOnly,
      meta: { title: "Запросы на доступ" }
    },
    {
      path: "/users",
      component: () => import("@/components/users/Users"),
      beforeEnter: adminOnly,
      meta: { title: "Пользователи" }
    },
    {
      path: "/manage-api",
      component: () => import("@/components/api/ManageApi"),
      beforeEnter: adminOrEditor,
      meta: { title: "API" }
    },
    {
      path: "/*",
      redirect: "/rooms"
    }
  ],
  mode: "history"
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title;
  next();
});

export default router;
