<script setup>
import Dialog from "primevue/dialog";

import { useConfirm } from "@/composables/useConfirm";
import { makeDialogPt } from "@/lib/prime-pt";

const { confirmState, settle } = useConfirm();
const dialogPt = makeDialogPt("max-w-md");
</script>

<template>
  <Dialog
    v-model:visible="confirmState.open"
    :header="confirmState.title"
    :modal="true"
    :closable="true"
    :draggable="false"
    :pt="dialogPt"
    @hide="settle(false)"
  >
    <p class="text-sm leading-6 text-steel-700">{{ confirmState.message }}</p>

    <template #footer>
      <div class="flex justify-end gap-3">
        <button
          v-if="confirmState.showCancel"
          type="button"
          class="rounded-xl border border-steel-200 bg-white px-4 py-2 text-sm font-medium text-steel-700 transition hover:bg-steel-100"
          @click="settle(false)"
        >
          {{ confirmState.cancelLabel }}
        </button>
        <button
          type="button"
          class="rounded-xl px-4 py-2 text-sm font-semibold text-white transition"
          :class="confirmState.danger ? 'bg-brand-600 hover:bg-brand-700' : 'bg-brand-500 hover:bg-brand-700'"
          @click="settle(true)"
        >
          {{ confirmState.confirmLabel }}
        </button>
      </div>
    </template>
  </Dialog>
</template>
