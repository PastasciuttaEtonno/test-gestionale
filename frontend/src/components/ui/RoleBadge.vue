<script setup>
defineProps({
  roleCode: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <span class="badge-ruolo">{{ roleCode || "n/d" }}</span>
</template>
