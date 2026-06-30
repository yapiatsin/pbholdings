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

    function renderItem(notif, alertsUrl) {
        var href = notif.lien || alertsUrl || '#';
        var unreadClass = notif.lu ? '' : ' pb-notification-item--unread';
        return (
            '<a href="' + escapeHtml(href) + '" class="pb-notification-item' + unreadClass + '" data-notification-id="' + notif.id + '">' +
            '<div class="pb-notification-item__title">' + titleFor(notif) + '</div>' +
            '<div class="pb-notification-item__message">' + escapeHtml(notif.message || '') + '</div>' +
            '<div class="pb-notification-item__time">' + escapeHtml(notif.created_at || '') + '</div>' +
            '</a>'
        );
    }

    function renderList(root, notifications, alertsUrl) {
        var listEl = root.querySelector('#pb-notifications-list');
        if (!listEl) {
            return;
        }
        if (!notifications.length) {
            listEl.innerHTML =
                '<div class="pb-notification-empty" id="pb-notifications-empty">' +
                'Aucune notification pour le moment.</div>';
            return;
        }
        listEl.innerHTML = notifications.map(function (notif) {
            return renderItem(notif, alertsUrl);
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
        }
    }

    function postJson(url) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
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
        if (!root) {
            return;
        }

        var listUrl = root.dataset.listUrl;
        var readUrlTemplate = root.dataset.readUrlTemplate;
        var readAllUrl = root.dataset.readAllUrl;
        var alertsUrl = root.dataset.alertsUrl;
        var pollInterval = 25000;
        var pollTimer = null;

        function refresh() {
            return fetch(listUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status);
                    }
                    return response.json();
                })
                .then(function (data) {
                    updateBadge(root, data.unread_count || 0);
                    renderList(root, data.notifications || [], alertsUrl);
                })
                .catch(function () { /* silencieux */ });
        }

        function markRead(notificationId) {
            if (!notificationId || !readUrlTemplate) {
                return Promise.resolve();
            }
            var url = readUrlTemplate.replace('/0/', '/' + notificationId + '/');
            return postJson(url).then(function () {
                return refresh();
            });
        }

        root.addEventListener('click', function (event) {
            var markAllBtn = event.target.closest('#pb-notifications-mark-all');
            if (markAllBtn) {
                event.preventDefault();
                event.stopPropagation();
                postJson(readAllUrl).then(function () {
                    return refresh();
                });
                return;
            }

            var item = event.target.closest('.pb-notification-item');
            if (item && item.dataset.notificationId) {
                var notifId = item.dataset.notificationId;
                var href = item.getAttribute('href');
                event.preventDefault();
                markRead(notifId).finally(function () {
                    if (href && href !== '#') {
                        window.location.href = href;
                    }
                });
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNotifications);
    } else {
        initNotifications();
    }
})();
