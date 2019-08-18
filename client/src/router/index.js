import Vue from "vue";
import Router from "vue-router";
import { adminOnly, authRequired } from "./authGuard";

import Rooms from "@/components/campus/Rooms";
import Login from "@/components/auth/Login";
import Register from "@/components/auth/Register";
import AccessRequests from "@/components/users/AccessRequests";
import Users from "@/components/users/Users";

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: "/",
      redirect: "/login"
    },
    {
      path: "/login",
      component: Login
    },
    {
      path: "/register",
      component: Register
    },
    {
      path: "/rooms",
      component: Rooms,
      beforeEnter: authRequired
    },
    {
      path: "/access_requests",
      component: AccessRequests,
      beforeEnter: adminOnly
    },
    {
      path: "/users",
      component: Users,
      beforeEnter: adminOnly
    }
  ],
  mode: "history"
});
