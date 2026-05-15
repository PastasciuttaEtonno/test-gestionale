<script setup>
import { computed } from "vue";

const props = defineProps({
  highlight: {
    type: Boolean,
    default: false,
  },
});

const classi = computed(() =>
  props.highlight ? "card-pannello-evidenza" : "card-pannello",
);
</script>

<template>
  <section :class="classi">
    <slot />
  </section>
</template>
