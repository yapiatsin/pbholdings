(function () {
    'use strict';

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : '';
    }

    function escapeHtml(text) {
        return String(text == null ? '' : text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function csrfToken() {
        return getCookie('csrftoken');
    }

    function urlFor(tpl, id) {
        return (tpl || '').replace('/0/', '/' + id + '/');
    }

    function postJson(url) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': csrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(function (res) {
            if (!res.ok) throw new Error('http');
            return res.json();
        });
    }

    function titleFor(notif) {
        if (notif.vehicule) {
            return (notif.label || notif.titre || '') + ' — ' + notif.vehicule;
        }
        return notif.titre || 'Notification';
    }

    function boot() {
        var root = document.getElementById('pb-notif-inbox');
        if (!root || root.dataset.bound === '1') return;
        root.dataset.bound = '1';

        var inboxUrl = root.getAttribute('data-inbox-url');
        var readTpl = root.getAttribute('data-read-url-template');
        var unreadTpl = root.getAttribute('data-unread-url-template');
        var readAllUrl = root.getAttribute('data-read-all-url');
        var selectedId = root.getAttribute('data-selected-id') || '';
        var filterStatus = '';

        var itemsEl = document.getElementById('pb-notif-items');
        var badgeEl = document.getElementById('pb-notif-pending-badge');
        var emptyEl = document.getElementById('pb-notif-empty');
        var detailEl = document.getElementById('pb-notif-detail');
        var titleEl = document.getElementById('pb-notif-detail-title');
        var statusEl = document.getElementById('pb-notif-detail-status');
        var threadEl = document.getElementById('pb-notif-thread');
        var markReadBtn = document.getElementById('pb-notif-mark-read');
        var markUnreadBtn = document.getElementById('pb-notif-mark-unread');
        var markAllBtn = document.getElementById('pb-notif-mark-all');
        var openBtn = document.getElementById('pb-notif-open');
        var statsRoot = document.getElementById('pb-notif-stats');
        var selected = null;

        function setBadge(n) {
            if (badgeEl) {
                if (n > 0) {
                    badgeEl.hidden = false;
                    badgeEl.textContent = String(n);
                } else {
                    badgeEl.hidden = true;
                }
            }
            if (markAllBtn) markAllBtn.hidden = n <= 0;
        }

        function setStats(stats) {
            if (!statsRoot || !stats) return;
            var values = [stats.total, stats.non_lues, stats.lues, stats.alertes];
            var els = statsRoot.querySelectorAll('.pb-kpi__value');
            values.forEach(function (value, index) {
                if (els[index]) els[index].textContent = String(value != null ? value : 0);
            });
        }

        function renderList(items) {
            if (!itemsEl) return;
            if (!items.length) {
                itemsEl.innerHTML = '<p class="pb-notif-empty-list">Aucune notification pour ce filtre.</p>';
                return;
            }
            itemsEl.innerHTML = items.map(function (n) {
                var active = String(n.id) === String(selectedId) ? ' is-active' : '';
                var unread = n.lu ? '' : ' pb-notif-item--unread';
                return (
                    '<button type="button" class="pb-notif-item' + active + unread + '" data-id="' + n.id + '">' +
                        '<div class="pb-notif-item__top">' +
                            '<span class="pb-notif-item__name">' + escapeHtml(titleFor(n)) + '</span>' +
                            '<span class="pb-notif-item__time">' + escapeHtml(n.created_at || '') + '</span>' +
                        '</div>' +
                        '<p class="pb-notif-item__preview">' + escapeHtml(n.message || '') + '</p>' +
                        '<span class="pb-notif-item__status' + (n.lu ? '' : ' pb-notif-item__status--unread') + '">' +
                            (n.lu ? 'Lue' : 'Non lue') +
                        '</span>' +
                    '</button>'
                );
            }).join('');
        }

        function renderDetail(notif) {
            selected = notif || null;
            if (!notif) {
                if (detailEl) detailEl.hidden = true;
                if (emptyEl) emptyEl.hidden = false;
                return;
            }
            if (emptyEl) emptyEl.hidden = true;
            if (detailEl) detailEl.hidden = false;
            if (titleEl) titleEl.textContent = titleFor(notif);
            if (statusEl) {
                statusEl.textContent = (notif.lu ? 'Lue' : 'Non lue') +
                    ' • ' + (notif.categorie_label || notif.type_label || '') +
                    (notif.created_at ? ' • ' + notif.created_at : '');
            }
            if (threadEl) {
                threadEl.innerHTML =
                    '<article class="pb-notif-detail-card">' +
                        '<p>' + escapeHtml(notif.message || '') + '</p>' +
                        '<ul class="pb-notif-detail-meta">' +
                            '<li>' + escapeHtml(notif.type_label || '') + '</li>' +
                            '<li>' + escapeHtml(notif.categorie_label || '') + '</li>' +
                            (notif.vehicule ? '<li>' + escapeHtml(notif.vehicule) + '</li>' : '') +
                            (notif.jours != null && notif.jours !== '' ? '<li>' + escapeHtml(notif.jours) + ' j</li>' : '') +
                        '</ul>' +
                    '</article>';
            }
            if (markReadBtn) markReadBtn.hidden = !!notif.lu;
            if (markUnreadBtn) markUnreadBtn.hidden = !notif.lu;
            if (openBtn) {
                openBtn.hidden = !notif.lien;
                openBtn.setAttribute('data-href', notif.lien || '');
            }
        }

        function refresh() {
            var params = new URLSearchParams();
            if (filterStatus) params.set('status', filterStatus);
            if (selectedId) params.set('id', selectedId);
            var qs = params.toString();
            return fetch(inboxUrl + (qs ? ('?' + qs) : ''), {
                credentials: 'same-origin',
                headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (!data || !data.ok) return;
                    setBadge(data.unread_count || 0);
                    setStats(data.stats);
                    renderList(data.notifications || []);
                    if (selectedId && data.selected) {
                        renderDetail(data.selected);
                    } else if (!selectedId) {
                        renderDetail(null);
                    }
                })
                .catch(function () {});
        }

        function selectNotification(id, markRead) {
            selectedId = String(id || '');
            root.setAttribute('data-selected-id', selectedId);
            var done = Promise.resolve();
            if (markRead && selectedId) {
                done = postJson(urlFor(readTpl, selectedId)).catch(function () {});
            }
            return done.then(refresh);
        }

        itemsEl.addEventListener('click', function (event) {
            var btn = event.target.closest('.pb-notif-item');
            if (!btn) return;
            selectNotification(btn.getAttribute('data-id'), true);
        });

        if (markReadBtn) {
            markReadBtn.addEventListener('click', function () {
                if (!selectedId) return;
                postJson(urlFor(readTpl, selectedId)).then(refresh);
            });
        }
        if (markUnreadBtn) {
            markUnreadBtn.addEventListener('click', function () {
                if (!selectedId) return;
                postJson(urlFor(unreadTpl, selectedId)).then(refresh);
            });
        }
        if (openBtn) {
            openBtn.addEventListener('click', function () {
                var href = openBtn.getAttribute('data-href');
                if (href) window.location.href = href;
            });
        }
        if (markAllBtn) {
            markAllBtn.addEventListener('click', function () {
                postJson(readAllUrl).then(refresh);
            });
        }

        root.querySelectorAll('.pb-notif-filter').forEach(function (btn) {
            btn.addEventListener('click', function () {
                root.querySelectorAll('.pb-notif-filter').forEach(function (item) {
                    item.classList.remove('is-active');
                });
                btn.classList.add('is-active');
                filterStatus = btn.getAttribute('data-filter') || '';
                refresh();
            });
        });

        if (selectedId) {
            selectNotification(selectedId, true);
        } else {
            refresh();
        }
    }

    document.addEventListener('pb:livepage', function () {
        var root = document.getElementById('pb-notif-inbox');
        if (root) delete root.dataset.bound;
        boot();
    });
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
