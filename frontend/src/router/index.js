import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "../stores/auth";
import AdminOnlyView from "../views/AdminOnlyView.vue";
import AnagraficaDetailView from "../views/AnagraficaDetailView.vue";
import AnagraficheView from "../views/AnagraficheView.vue";
import ArticoliView from "../views/ArticoliView.vue";
import ArticoloDetailView from "../views/ArticoloDetailView.vue";
import BollaDetailView from "../views/BollaDetailView.vue";
import BolleView from "../views/BolleView.vue";
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
        titolo: "Accesso",
        guestOnly: true,
        hideShell: true,
      },
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardView,
      meta: {
        titolo: "Dashboard",
        requiresAuth: true,
      },
    },
    {
      path: "/anagrafiche",
      name: "anagrafiche",
      component: AnagraficheView,
      meta: {
        titolo: "Anagrafiche",
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
        titolo: "Scheda anagrafica",
        requiresAuth: true,
        requiredPermissions: ["anagrafiche.read"],
      },
    },
    {
      path: "/articoli",
      name: "articoli",
      component: ArticoliView,
      meta: {
        titolo: "Articoli",
        requiresAuth: true,
        requiredPermissions: ["articoli.read"],
      },
    },
    {
      path: "/articoli/:id",
      name: "articolo-detail",
      component: ArticoloDetailView,
      props: true,
      meta: {
        titolo: "Scheda articolo",
        requiresAuth: true,
        requiredPermissions: ["articoli.read"],
      },
    },
    {
      path: "/bolle",
      name: "bolle",
      component: BolleView,
      meta: {
        titolo: "Bolle",
        requiresAuth: true,
        requiredPermissions: ["bolle.read"],
      },
    },
    {
      path: "/bolle/:id",
      name: "bolla-detail",
      component: BollaDetailView,
      props: true,
      meta: {
        titolo: "Bolla",
        requiresAuth: true,
        requiredPermissions: ["bolle.read"],
      },
    },
    {
      path: "/admin-only",
      name: "admin-only",
      component: AdminOnlyView,
      meta: {
        titolo: "Area amministratore",
        requiresAuth: true,
        requiredRoles: ["admin"],
      },
    },
    {
      path: "/tenant-admin",
      name: "tenant-admin",
      component: TenantAdminView,
      meta: {
        titolo: "Amministrazione tenant",
        requiresAuth: true,
        requiredRoles: ["tenant_admin"],
      },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFoundView,
      meta: {
        titolo: "Pagina non trovata",
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

// Il titolo del documento era "Gestionale Auth Client" su ogni rotta: nella
// cronologia e fra le schede le pagine erano indistinguibili, e chi naviga con
// uno screen reader non riceveva nessun segnale di cambio pagina.
router.afterEach((to) => {
  document.title = to.meta.titolo
    ? `${to.meta.titolo} · Gestionale`
    : "Gestionale";
});

export default router;
