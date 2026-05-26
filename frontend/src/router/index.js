import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "../stores/auth";
import AdminOnlyView from "../views/AdminOnlyView.vue";
import AnagraficaDetailView from "../views/AnagraficaDetailView.vue";
import AnagraficheView from "../views/AnagraficheView.vue";
import DashboardView from "../views/DashboardView.vue";
import LoginView from "../views/LoginView.vue";
import NotFoundView from "../views/NotFoundView.vue";
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
        hideShell: true,
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
      path: "/anagrafiche",
      name: "anagrafiche",
      component: AnagraficheView,
      meta: {
        requiresAuth: true,
        requiredPermissions: ["anagrafiche.read"],
      },
    },
    {
      path: "/anagrafiche/:id",
      name: "anagrafica-detail",
      component: AnagraficaDetailView,
      props: true,
      meta: {
        requiresAuth: true,
        requiredPermissions: ["anagrafiche.read"],
      },
    },
    {
      path: "/admin-only",
      name: "admin-only",
      component: AdminOnlyView,
      meta: {
        requiresAuth: true,
        requiredRoles: ["admin"],
      },
    },
    {
      path: "/tenant-admin",
      name: "tenant-admin",
      component: TenantAdminView,
      meta: {
        requiresAuth: true,
        requiredRoles: ["tenant_admin"],
      },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFoundView,
      meta: {
        hideShell: true,
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

  if (to.meta.requiredRoles && !authStore.hasRole(...to.meta.requiredRoles)) {
    return { name: "dashboard" };
  }

  if (
    to.meta.requiredPermissions &&
    !authStore.hasEveryPermission(to.meta.requiredPermissions)
  ) {
    return { name: "dashboard" };
  }

  return true;
});

export default router;
