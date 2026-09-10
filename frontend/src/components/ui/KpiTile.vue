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
  <div class="rounded-2xl border border-steel-200 bg-steel-50 p-3 sm:p-4">
    <p class="etichetta-dato">{{ label }}</p>
    <p class="mt-3 text-2xl font-semibold text-steel-900 sm:text-3xl">{{ value }}</p>
    <p class="mt-2 text-sm text-steel-700">{{ note }}</p>
  </div>
</template>
