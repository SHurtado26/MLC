// Tabs, botones flotantes de interpretación, e imágenes con fallback grácil.
// JS plano en assets/ (Dash lo sirve automáticamente) — no requiere callbacks
// de servidor para interacciones puramente de UI.

// Dash es una SPA de React: los botones de tabs no existen todavía cuando
// dispara 'DOMContentLoaded', así que se delega en document (igual que los
// botones flotantes de interpretación) en vez de atar listeners directos.
document.addEventListener('click', function (e) {
  var btn = e.target.closest('.tab-btn');
  if (!btn) return;
  var name = btn.id.replace('tab-btn-', '');
  document.querySelectorAll('.tab-panel').forEach(function (el) { el.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function (el) { el.classList.remove('active'); });
  var panel = document.getElementById('tab-' + name);
  if (panel) panel.classList.add('active');
  btn.classList.add('active');
  document.querySelectorAll('.info-pop.open').forEach(function (el) { el.classList.remove('open'); });

  if (name === 'eda' && window.Plotly) {
    requestAnimationFrame(function () {
      document.querySelectorAll('#tab-eda .js-plotly-plot').forEach(function (el) {
        Plotly.Plots.resize(el);
      });
    });
  }
});

// Botones flotantes "i" — delegado en document para funcionar tras cualquier
// re-render de Dash.
document.addEventListener('click', function (e) {
  var btn = e.target.closest('.info-fab');
  if (btn) {
    var id = btn.dataset.target;
    var pop = document.getElementById(id);
    if (!pop) return;
    var isOpen = pop.classList.contains('open');
    document.querySelectorAll('.info-pop.open').forEach(function (el) { el.classList.remove('open'); });
    if (!isOpen) pop.classList.add('open');
    return;
  }
  if (!e.target.closest('.chart-card')) {
    document.querySelectorAll('.info-pop.open').forEach(function (el) { el.classList.remove('open'); });
  }
});

// Oculta con gracia los bloques de imagen (logos, bandera, junta) mientras
// el archivo todavía no se ha guardado en assets/.
document.addEventListener('error', function (e) {
  var el = e.target;
  if (el.tagName !== 'IMG') return;
  if (el.classList.contains('logo-img')) {
    var badge = el.closest('.logo-badge');
    if (badge) badge.style.display = 'none';
  } else if (el.classList.contains('flag-icon')) {
    el.style.display = 'none';
  }
}, true);
