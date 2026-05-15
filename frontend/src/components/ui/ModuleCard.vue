<script setup>
import BaseButton from "./BaseButton.vue";
import SectionLabel from "./SectionLabel.vue";

defineProps({
  area: {
    type: String,
    default: "",
  },
  title: {
    type: String,
    default: "",
  },
  description: {
    type: String,
    default: "",
  },
  metrics: {
    type: Array,
    default: () => [],
  },
  actions: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <article class="rounded-[1.5rem] border border-steel-200 bg-white p-6 shadow-panel">
    <SectionLabel>{{ area }}</SectionLabel>
    <h3 class="mt-3 text-2xl font-semibold text-steel-900">{{ title }}</h3>
    <p class="mt-3 text-sm leading-6 text-steel-700">{{ description }}</p>

    <div class="mt-6 grid gap-3 sm:grid-cols-2">
      <div
        v-for="metric in metrics"
        :key="metric.label"
        class="rounded-2xl border border-steel-200 bg-steel-50 px-4 py-3"
      >
        <p class="text-xs uppercase tracking-[0.18em] text-steel-400">{{ metric.label }}</p>
        <p class="mt-2 text-lg font-semibold text-steel-900">{{ metric.value }}</p>
      </div>
    </div>

    <div class="mt-6 flex flex-wrap gap-3">
      <BaseButton
        v-for="action in actions"
        :key="action"
        type="button"
        variant="secondary"
      >
        {{ action }}
      </BaseButton>
    </div>
  </article>
</template>
