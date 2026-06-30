/**
 * P&BEntreprise — Tracking automatique des clics
 * Écoute tous les clics sur liens et boutons et envoie l'info à /track-click/
 * (insère ce script avant </body> sur toutes les pages publiques).
 */
(function () {
    var ENDPOINT = '/track-click/';

    function getCookie(name) {
        var v = '; ' + document.cookie;
        var parts = v.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift();
        return '';
    }

    function sendClick(element) {
        try {
            var data = new FormData();
            data.append('element', element);
            data.append('url_page', window.location.pathname);
            data.append('csrfmiddlewaretoken', getCookie('csrftoken'));

            if (navigator.sendBeacon) {
                navigator.sendBeacon(ENDPOINT, data);
            } else {
                fetch(ENDPOINT, {
                    method: 'POST',
                    body: data,
                    credentials: 'same-origin',
                    keepalive: true
                }).catch(function () {});
            }
        } catch (e) { /* no-op */ }
    }

    document.addEventListener('click', function (e) {
        var target = e.target.closest('a, button, [data-track]');
        if (!target) return;
        var label = (target.getAttribute('data-track') ||
                     target.textContent || '').trim().substring(0, 150);
        var href = target.getAttribute('href') || '';
        var id = target.id ? '#' + target.id : '';
        var element = (label || target.tagName) + id + (href ? ' → ' + href : '');
        sendClick(element.substring(0, 200));
    }, true);
})();
