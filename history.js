'use strict';
function createMarketHistory(initial, onChange) {
  let points = [], hours = 24, end = Date.now(), loading = false;
  const day = 24 * 60 * 60 * 1000;
  function publish(incoming = []) {
    end = Date.now();
    const byTime = new Map();
    for (const p of [...points, ...incoming]) {
      if (p && Number.isFinite(p.p) && p.p > 0 && Number.isFinite(p.t) && p.t >= end - day && p.t <= end) byTime.set(p.t, p);
    }
    points = [...byTime.values()].sort((a, b) => a.t - b.t);
    try { localStorage.setItem('elytra_history', JSON.stringify(points)); } catch {}
    onChange(points.filter(p => p.t >= end - hours * 3600000));
  }
  try {
    const cached = JSON.parse(localStorage.getItem('elytra_history') || '[]');
    if (Array.isArray(cached)) points = cached;
  } catch {}
  points = points.concat(Array.isArray(initial) ? initial : []);
  return {
    start: () => end - hours * 3600000,
    end: () => end,
    setHours(value) { hours = value === 1 ? 1 : 24; publish(); },
    record(point) { publish([point]); },
    async refresh() {
      if (loading) return;
      loading = true;
      try {
        const response = await fetch('/api/history', {cache: 'no-store'});
        if (!response.ok) throw Error('History unavailable');
        const data = await response.json();
        if (!Array.isArray(data.history)) throw Error('Invalid history');
        publish(data.history);
      } catch { publish(); }
      finally { loading = false; }
    }
  };
}
