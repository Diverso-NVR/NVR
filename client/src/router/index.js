import Vue from "vue";
import Router from "vue-router";
import { adminOnly, authRequired } from "./authGuard";

import ManageApi from "@/components/api/ManageApi";
import Rooms from "@/components/campus/Rooms";
import Streaming from "@/components/campus/Streaming";
import Login from "@/components/auth/Login";
import Register from "@/components/auth/Register";
import AccessRequests from "@/components/users/AccessRequests";
import Users from "@/components/users/Users";

Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: "/",
      redirect: "/rooms"
    },
    {
      path: "/login",
      component: Login,
      meta: { title: "Вход" }
    },
    {
      path: "/register",
      component: Register,
      meta: { title: "Регистрация" }
    },
    {
      path: "/rooms",
      component: Rooms,
      beforeEnter: authRequired,
      meta: { title: "Аудитории" }
    },
    {
      path: "/streaming",
      component: Streaming,
      beforeEnter: authRequired,
      meta: { title: "Стриминг" }
    },
    {
      path: "/access-requests",
      component: AccessRequests,
      beforeEnter: adminOnly,
      meta: { title: "Запросы на доступ" }
    },
    {
      path: "/users",
      component: Users,
      beforeEnter: adminOnly,
      meta: { title: "Пользователи" }
    },
    {
      path: "/manage-api",
      component: ManageApi,
      beforeEnter: adminOnly,
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
