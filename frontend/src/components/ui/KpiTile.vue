<script setup>
defineProps({
  label: {
    type: String,
    default: "",
  },
  value: {
    type: String,
    default: "",
  },
  note: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <div class="rounded-2xl border border-steel-200 bg-steel-50 p-4">
    <p class="text-xs uppercase tracking-[0.2em] text-steel-400">{{ label }}</p>
    <p class="mt-3 text-3xl font-semibold text-steel-900">{{ value }}</p>
    <p class="mt-2 text-sm text-steel-700">{{ note }}</p>
  </div>
</template>
