import { defineStore } from "pinia";
import { ref } from "vue";

export const useEventsStore = defineStore("events", () => {
  const connected = ref(false);
  let _source = null;
  const _handlers = new Map();

  function on(eventType, handler) {
    if (!_handlers.has(eventType)) _handlers.set(eventType, []);
    _handlers.get(eventType).push(handler);
    return () => {
      const list = _handlers.get(eventType) || [];
      _handlers.set(eventType, list.filter((h) => h !== handler));
    };
  }

  function _dispatch(event) {
    (_handlers.get(event.type) || []).forEach((h) => h(event));
    (_handlers.get("*") || []).forEach((h) => h(event));
  }

  function connect(token) {
    if (_source) return;

    const url = `/api/v1/events/stream?token=${encodeURIComponent(token)}`;
    _source = new EventSource(url);

    _source.onopen = () => {
      connected.value = true;
    };

    _source.onmessage = (e) => {
      try {
        _dispatch(JSON.parse(e.data));
      } catch {
        // messaggio non JSON (es. heartbeat comment ignorato)
      }
    };

    _source.onerror = () => {
      connected.value = false;
      // EventSource del browser gestisce il reconnect automaticamente
    };
  }

  function disconnect() {
    _source?.close();
    _source = null;
    connected.value = false;
  }

  return { connected, connect, disconnect, on };
});
