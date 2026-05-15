import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "../stores/auth";
import AdminOnlyView from "../views/AdminOnlyView.vue";
import DashboardView from "../views/DashboardView.vue";
import LoginView from "../views/LoginView.vue";
import TenantAdminView from "../views/TenantAdminView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/dashboard",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: {
        guestOnly: true,
      },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: "/admin-only",
      name: "admin-only",
      component: AdminOnlyView,
      meta: {
        requiresAuth: true,
        requiresSuperAdmin: true,
      },
    },
    {
      path: "/tenant-admin",
      name: "tenant-admin",
      component: TenantAdminView,
      meta: {
        requiresAuth: true,
        requiresTenantAdmin: true,
      },
    },
  ],
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();

  if (!authStore.isInitialized) {
    await authStore.initialize();
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: "dashboard" };
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: "login",
      query: {
        redirect: to.fullPath,
      },
    };
  }

  if (to.meta.requiresSuperAdmin && authStore.user?.role_code !== "admin") {
    return { name: "dashboard" };
  }

  if (to.meta.requiresTenantAdmin && authStore.user?.role_code !== "tenant_admin") {
    return { name: "dashboard" };
  }

  return true;
});

export default router;
