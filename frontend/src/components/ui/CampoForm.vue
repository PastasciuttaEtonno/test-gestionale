<script setup>
import { computed, useId } from "vue";

/**
 * Coppia label + controllo con l'id generato una volta sola.
 *
 * Le label scritte a mano nelle viste erano visivamente accanto al campo ma
 * non collegate: il click sulla label non portava il fuoco e uno screen
 * reader leggeva il placeholder. Qui l'id nasce insieme al campo e arriva al
 * controllo tramite lo slot, quindi la coppia non puo' piu' scollegarsi.
 */

const props = defineProps({
  label: { type: String, required: true },
  obbligatorio: { type: Boolean, default: false },
  // Formato atteso, mostrato sotto il campo e annunciato con esso.
  aiuto: { type: String, default: "" },
  errore: { type: String, default: "" },
});

const id = useId();
const idLabel = `${id}-label`;
const idAiuto = `${id}-aiuto`;
const idErrore = `${id}-errore`;

const descrittoDa = computed(
  () =>
    [props.aiuto ? idAiuto : null, props.errore ? idErrore : null]
      .filter(Boolean)
      .join(" ") || undefined,
);

// Un solo oggetto da spargere sul controllo, cosi' le viste non devono
// ricordarsi quali attributi servono.
const campo = computed(() => ({
  id,
  "aria-describedby": descrittoDa.value,
  "aria-invalid": props.errore ? "true" : undefined,
  "aria-required": props.obbligatorio ? "true" : undefined,
}));

// PrimeVue Select non rende un <input>: il focus sta su uno <span
// role="combobox">, che `label[for]` non puo' associare. Per quel caso il
// collegamento passa da aria-labelledby.
const combo = computed(() => ({
  inputId: id,
  ariaLabelledby: idLabel,
  ariaDescribedby: descrittoDa.value,
}));
</script>

<template>
  <div>
    <label
      :id="idLabel"
      :for="id"
      class="etichetta-campo"
    >
      {{ label }}<span v-if="obbligatorio" aria-hidden="true"> *</span>
      <span v-if="obbligatorio" class="sr-only"> (obbligatorio)</span>
    </label>

    <slot :id="id" :campo="campo" :combo="combo" :descritto-da="descrittoDa" />

    <p v-if="aiuto" :id="idAiuto" class="mt-1 text-xs text-steel-600">
      {{ aiuto }}
    </p>
    <p v-if="errore" :id="idErrore" class="mt-1 text-xs text-brand-700">
      {{ errore }}
    </p>
  </div>
</template>
