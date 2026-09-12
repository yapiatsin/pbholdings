(function () {
    'use strict';

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function escapeHtml(text) {
        if (!text) {
            return '';
        }
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    var csrftoken = getCookie('csrftoken');

    function titleFor(notif) {
        if (notif.vehicule) {
            var label = notif.label || notif.titre || '';
            return escapeHtml(label + ' — ' + notif.vehicule);
        }
        return escapeHtml(notif.titre || '');
    }

    function pageUrlFor(root, notifId) {
        var pageUrl = root.dataset.pageUrl || '/pbentreprise/notifications/';
        return pageUrl.replace(/\/?$/, '/') + notifId + '/';
    }

    function renderItem(root, notif) {
        return (
            '<a href="' + escapeHtml(pageUrlFor(root, notif.id)) + '" class="pb-notification-item pb-notification-item--unread" data-notification-id="' + notif.id + '">' +
            '<div class="pb-notification-item__title">' + titleFor(notif) + '</div>' +
            '<div class="pb-notification-item__message">' + escapeHtml(notif.message || '') + '</div>' +
            '<div class="pb-notification-item__time">' + escapeHtml(notif.created_at || '') + '</div>' +
            '</a>'
        );
    }

    function renderList(root, notifications) {
        var listEl = root.querySelector('#pb-notifications-list');
        if (!listEl) {
            return;
        }
        var unread = (notifications || []).filter(function (notif) {
            return !notif.lu;
        });
        if (!unread.length) {
            listEl.innerHTML =
                '<div class="pb-notification-empty" id="pb-notifications-empty">' +
                'Aucune notification non lue.</div>';
            return;
        }
        listEl.innerHTML = unread.map(function (notif) {
            return renderItem(root, notif);
        }).join('');
    }

    function updateBadge(root, unreadCount) {
        var badge = root.querySelector('#pb-notifications-badge');
        var markAll = root.querySelector('#pb-notifications-mark-all');
        if (badge) {
            badge.textContent = unreadCount;
            badge.classList.toggle('d-none', unreadCount <= 0);
        }
        if (markAll) {
            markAll.classList.toggle('d-none', unreadCount <= 0);
            markAll.disabled = unreadCount <= 0;
        }
    }

    function applyPayload(root, data) {
        updateBadge(root, data.unread_count || 0);
        renderList(root, data.notifications || []);
    }

    function postJson(url) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            credentials: 'same-origin',
        }).then(function (response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            return response.json();
        });
    }

    function initNotifications() {
        var root = document.getElementById('pb-notifications-root');
        if (!root || root.dataset.bound === '1') {
            return;
        }
        root.dataset.bound = '1';

        var listUrl = root.dataset.listUrl;
        var readAllUrl = root.dataset.readAllUrl;
        var pageUrl = root.dataset.pageUrl;
        var pollInterval = 25000;
        var pollTimer = null;

        function refresh() {
            return fetch(listUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
                credentials: 'same-origin',
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status);
                    }
                    return response.json();
                })
                .then(function (data) {
                    applyPayload(root, data);
                })
                .catch(function () { /* silencieux */ });
        }

        root.addEventListener('click', function (event) {
            var markAllBtn = event.target.closest('#pb-notifications-mark-all');
            if (markAllBtn) {
                event.preventDefault();
                event.stopPropagation();
                if (markAllBtn.disabled) return;
                markAllBtn.disabled = true;
                applyPayload(root, { unread_count: 0, notifications: [] });
                postJson(readAllUrl)
                    .then(function (data) {
                        applyPayload(root, data);
                    })
                    .catch(function () {
                        markAllBtn.disabled = false;
                        refresh();
                    });
                return;
            }

            var footer = event.target.closest('#pb-notifications-footer');
            if (footer) {
                return;
            }

            var item = event.target.closest('.pb-notification-item');
            if (item && item.dataset.notificationId) {
                event.preventDefault();
                event.stopPropagation();
                var href = item.getAttribute('href') || (pageUrl + item.dataset.notificationId + '/');
                window.location.href = href;
            }
        });

        var toggle = root.querySelector('#pb-notifications-toggle');
        if (toggle) {
            toggle.addEventListener('click', function () {
                refresh();
            });
        }

        document.addEventListener('visibilitychange', function () {
            if (!document.hidden) {
                refresh();
            }
        });

        refresh();
        pollTimer = window.setInterval(refresh, pollInterval);
        window.addEventListener('beforeunload', function () {
            if (pollTimer) {
                window.clearInterval(pollTimer);
            }
        });
    }

    document.addEventListener('pb:livepage', function () {
        var root = document.getElementById('pb-notifications-root');
        if (root) delete root.dataset.bound;
        initNotifications();
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNotifications);
    } else {
        initNotifications();
    }
})();
