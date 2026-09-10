<script setup>
defineProps({
  title: {
    type: String,
    default: "",
  },
  items: {
    type: Array,
    default: () => [],
  },
  activeItem: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <section class="space-y-2">
    <p class="px-3 text-[11px] font-semibold uppercase tracking-[0.24em] text-white/55">
      {{ title }}
    </p>
    <div class="space-y-1.5">
      <button
        v-for="item in items"
        :key="item"
        type="button"
        class="group flex h-12 w-full items-center rounded-xl border border-transparent px-3 text-left text-sm font-medium text-white/76 transition hover:border-white/8 hover:bg-white/8 hover:text-white"
        :class="{
          'border-brand-300/22 bg-brand-500 text-white shadow-[0_10px_24px_-16px_rgba(198,40,40,0.9)]':
            item === activeItem,
        }"
      >
        <span
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/8 text-[11px] font-semibold uppercase tracking-[0.16em] text-white/72 transition group-hover:bg-white/12 group-hover:text-white"
          :class="{ 'bg-white/14 text-white': item === activeItem }"
        >
          {{ item.slice(0, 2) }}
        </span>
        <span class="ml-3 truncate">{{ item }}</span>
      </button>
    </div>
  </section>
</template>
