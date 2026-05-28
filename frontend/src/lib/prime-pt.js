// Shared PrimeVue passthrough (pt) presets, so an InputText / Select / IconField
// looks identical at every call site. Views compose these instead of redeclaring
// the full class strings.

export const ptIconField = { root: { class: "relative" } };

export const ptInputIcon = {
  root: {
    class: "pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-steel-400",
  },
};

const inputTextBase =
  "h-11 w-full rounded-xl border border-steel-200 bg-steel-50 pl-9 pr-4 text-sm text-steel-900 placeholder:text-steel-400 transition focus:border-brand-500 focus:bg-white focus:outline-none";

export function makePtInputText(extra = "") {
  return { root: { class: `${inputTextBase} ${extra}`.trim() } };
}

const selectShared = {
  label: { class: "flex-1 truncate px-4 text-steel-700" },
  dropdown: { class: "flex shrink-0 items-center justify-center pr-3 text-steel-400" },
  overlay: {
    class:
      "absolute left-0 top-full z-50 mt-1 min-w-full overflow-hidden rounded-xl border border-steel-200 bg-white shadow-lg",
  },
  listContainer: { class: "max-h-60 overflow-y-auto" },
  list: { class: "py-1" },
  option: {
    class:
      "cursor-pointer px-4 py-2.5 text-sm text-steel-700 transition hover:bg-brand-50 hover:text-brand-700",
  },
  optionLabel: { class: "" },
  emptyMessage: { class: "px-4 py-2.5 text-sm text-steel-400 italic" },
  clearIcon: { class: "mr-2 h-3.5 w-3.5 text-steel-400 hover:text-steel-700 transition" },
};

const selectRootBase =
  "relative flex h-11 cursor-pointer select-none items-center rounded-xl border border-steel-200 text-sm transition focus:outline-none";

export function makePtSelect(rootExtra = "", bg = "bg-steel-50") {
  return { root: { class: `${selectRootBase} ${bg} ${rootExtra}`.trim() }, ...selectShared };
}

// Dialog: unstyled PrimeVue gives no backdrop scrim and no panel background,
// so the modal renders see-through. This preset supplies both.
export function makeDialogPt(maxWidth = "max-w-2xl") {
  return {
    mask: {
      class:
        "fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-steel-900/50 p-4 sm:items-center",
    },
    root: {
      class: `w-full ${maxWidth} rounded-2xl border border-steel-200 bg-white shadow-panel`,
    },
    header: {
      class:
        "flex items-center justify-between gap-4 border-b border-steel-100 px-6 py-4 text-base font-semibold text-steel-900",
    },
    content: { class: "px-6 py-5" },
    footer: { class: "border-t border-steel-100 px-6 py-4" },
  };
}
