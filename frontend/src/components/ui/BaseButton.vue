<script setup>
import { computed } from "vue";

const props = defineProps({
  variant: {
    type: String,
    default: "primary",
  },
  type: {
    type: String,
    default: "button",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  block: {
    type: Boolean,
    default: false,
  },
});

const classi = computed(() => {
  const comuni =
    "inline-flex h-11 items-center justify-center rounded-xl px-4 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60";
  const larghezza = props.block ? " w-full" : "";

  if (props.variant === "secondary") {
    return `${comuni}${larghezza} border border-steel-200 bg-white text-steel-700 hover:bg-steel-100`;
  }

  return `${comuni}${larghezza} bg-brand-500 text-white hover:bg-brand-700`;
});
</script>

<template>
  <button :type="type" :disabled="disabled" :class="classi">
    <slot />
  </button>
</template>
