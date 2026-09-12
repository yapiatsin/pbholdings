(function () {
    var controller = null;
    var applying = false;

    document.addEventListener('alpine:init', function () {
        if (!window.Alpine || !Alpine.store) return;
        Alpine.store('pb', { busy: false });
    });

    function storeBusy(on) {
        try {
            if (window.Alpine && Alpine.store('pb')) Alpine.store('pb').busy = !!on;
        } catch (e) {}
    }

    function setBusy(on) {
        document.body.classList.toggle('pb-live-filter-busy', on);
        storeBusy(on);
    }

    function currentLayout() {
        return document.body.getAttribute('data-live-layout') || '';
    }

    function isPost(form) {
        return (form.getAttribute('method') || 'get').toLowerCase() === 'post';
    }

    function isFilterForm(form) {
        if (!form || form.tagName !== 'FORM' || isPost(form)) return false;
        if (form.hasAttribute('data-no-live-filter') || form.hasAttribute('data-no-live-nav')) return false;
        if (form.hasAttribute('data-live-search')) return false;
        if (form.classList.contains('pb-navbar-search-form')) return false;
        if (form.id === 'motifSortiForm' || form.id === 'loginForm') return false;
        if (form.hasAttribute('data-live-filter')) return true;
        if (form.id === 'basic-form') return true;
        if (form.classList.contains('pb-panel__filter') || form.classList.contains('search-form')) return true;
        return !!(form.querySelector('[name="date_debut"], [name="periode"], [name="categorie"], [name="immatriculation"]'));
    }

    function isAjaxManagedForm(form) {
        if (!form) return false;
        if (form.id && /UpdateForm$/i.test(form.id)) return true;
        if (form.closest('#modalBodyContent, #editCarModal, #editRecetteModal')) return true;
        return false;
    }

    function isLivePostForm(form) {
        if (!form || !isPost(form)) return false;
        if (form.hasAttribute('data-no-live-nav') || form.hasAttribute('data-live-search')) return false;
        if (form.id === 'loginForm' || form.id === 'motifSortiForm') return false;
        if (isAjaxManagedForm(form)) return false;
        return true;
    }

    function keepSearchParam(url) {
        if (url.searchParams.has('search')) return;
        try {
            var current = new URL(window.location.href).searchParams.get('search');
            if (current) url.searchParams.set('search', current);
        } catch (e) {}
    }

    function formToUrl(form) {
        var month = document.getElementById('month');
        var year = document.getElementById('year');
        var fm = form.querySelector('#form-month');
        var fy = form.querySelector('#form-year');
        if (month && fm) fm.value = month.value;
        if (year && fy) fy.value = year.value;

        var action = form.getAttribute('action') || window.location.href;
        var url = new URL(action, window.location.origin);
        var data = new FormData(form);
        url.search = '';
        data.forEach(function (value, key) {
            if (key === 'csrfmiddlewaretoken' || key === 'partial') return;
            if (value !== null && String(value).trim() !== '') url.searchParams.append(key, value);
        });
        keepSearchParam(url);
        return url;
    }

    function closeModals() {
        if (window.jQuery) {
            window.jQuery('.modal').modal('hide');
            window.jQuery('.modal-backdrop').remove();
            window.jQuery('body').removeClass('modal-open').css('padding-right', '');
        }
    }

    function shouldRunScript(script) {
        var src = script.getAttribute('src') || '';
        if (src.indexOf('saisie-live-search.js') !== -1) return false;
        if (src.indexOf('live-filter.js') !== -1) return false;
        if (src.indexOf('pb-live-app.js') !== -1) return false;
        if (src.indexOf('alpine.min.js') !== -1) return false;
        var code = script.textContent || '';
        if (!code.trim() && !src) return false;
        if (/\$\(\s*document\s*\)\.on/.test(code)) return false;
        return true;
    }

    // Déclarations de premier niveau d'un script inline : function, var, let, const.
    var TOP_LEVEL_DECL = /^[ \t]*(?:function[ \t]+|var[ \t]+|let[ \t]+|const[ \t]+)([A-Za-z_$][\w$]*)/gm;

    /**
     * Isole un script inline réexécuté dans sa propre portée.
     *
     * Réinjecté tel quel, il s'exécute dans la portée globale : à la deuxième
     * navigation vers la même page, ses `const`/`let` de premier niveau
     * (ctx, cta, ctxRepartition…) lèvent « Identifier 'x' has already been
     * declared » et le script entier s'interrompt — plus aucun graphique ne
     * se construit. On l'enveloppe donc dans une IIFE, puis on republie ses
     * déclarations de premier niveau sur window : les handlers inline
     * (onclick="selectMonthYear()") et les scripts qui se partagent une
     * variable d'un bloc à l'autre continuent de fonctionner, et une simple
     * réaffectation ne lève jamais d'erreur.
     */
    function scopedCode(code) {
        var noms = [];
        var m;
        TOP_LEVEL_DECL.lastIndex = 0;
        while ((m = TOP_LEVEL_DECL.exec(code)) !== null) {
            if (noms.indexOf(m[1]) === -1) noms.push(m[1]);
        }
        // try/catch : un nom capturé dans un bloc imbriqué n'existe pas ici.
        var exports = noms.map(function (nom) {
            return 'try { window.' + nom + ' = ' + nom + '; } catch (e) {}';
        }).join('\n');
        return '(function () {\n' + code + '\n' + exports + '\n})();';
    }

    function cloneScript(old) {
        var neu = document.createElement('script');
        Array.prototype.forEach.call(old.attributes, function (attr) {
            neu.setAttribute(attr.name, attr.value);
        });
        var code = old.textContent || '';
        // Les scripts externes (src) se rechargent tels quels : rien à isoler.
        neu.textContent = old.getAttribute('src') ? code : scopedCode(code);
        return neu;
    }

    function runScripts(scope) {
        if (!scope) return;
        scope.querySelectorAll('script').forEach(function (old) {
            if (!shouldRunScript(old)) return;
            old.parentNode.replaceChild(cloneScript(old), old);
        });
    }

    function runCustomJs(parsed) {
        var box = parsed.querySelector('[data-live-custom-js]');
        if (!box) return;
        box.querySelectorAll('script').forEach(function (old) {
            if (!shouldRunScript(old)) return;
            var neu = cloneScript(old);
            document.body.appendChild(neu);
            neu.parentNode.removeChild(neu);
        });
    }

    function destroyTables() {
        if (!window.jQuery || !window.jQuery.fn || !window.jQuery.fn.DataTable) return;
        var $ = window.jQuery;
        ['#example1', '#example2'].forEach(function (sel) {
            if ($.fn.DataTable.isDataTable(sel)) {
                try { $(sel).DataTable().destroy(); } catch (e) {}
            }
        });
    }

    function destroyCharts(scope) {
        if (!scope || !window.Chart || typeof window.Chart.getChart !== 'function') return;
        scope.querySelectorAll('canvas').forEach(function (canvas) {
            try {
                var inst = window.Chart.getChart(canvas);
                if (inst) inst.destroy();
            } catch (e) {}
        });
    }

    function reinitTables() {
        if (!window.jQuery || !window.jQuery.fn || !window.jQuery.fn.DataTable) return;
        var $ = window.jQuery;
        if (document.querySelector('#example1')) {
            try { $('#example1').DataTable(); } catch (e) {}
        }
        if (document.querySelector('#example2')) {
            try {
                $('#example2').DataTable({
                    paging: true,
                    lengthChange: false,
                    searching: false,
                    ordering: true,
                    info: true,
                    autoWidth: false
                });
            } catch (e) {}
        }
    }

    function markSidebar(url) {
        var sidebar = document.querySelector('.pb-sidebar-glass .nav-sidebar, .pb-sidebar .nav-sidebar');
        if (!sidebar) return;
        var current;
        try { current = new URL(url, window.location.origin).pathname.replace(/\/+$/, '') || '/'; }
        catch (e) { return; }
        sidebar.querySelectorAll('a.nav-link').forEach(function (link) {
            link.classList.remove('active');
        });
        sidebar.querySelectorAll('.has-treeview').forEach(function (item) {
            item.classList.remove('menu-open');
        });
        var links = Array.prototype.slice.call(sidebar.querySelectorAll('a.nav-link[href]'));
        var best = null;
        var bestLen = -1;
        links.forEach(function (link) {
            var href = link.getAttribute('href');
            if (!href || href === '#' || href.indexOf('javascript:') === 0) return;
            var path;
            try { path = new URL(link.href, window.location.origin).pathname.replace(/\/+$/, ''); }
            catch (e2) { return; }
            if (!path) return;
            if (current === path || (path.length > 12 && current.indexOf(path) === 0)) {
                if (path.length > bestLen) {
                    best = link;
                    bestLen = path.length;
                }
            }
        });
        if (!best) return;
        best.classList.add('active');
        var parent = best.closest('.has-treeview');
        if (parent) parent.classList.add('menu-open');
    }

    function showMessages(doc) {
        var el = doc.getElementById('pb-live-messages');
        if (!el || !window.Swal) return;
        var items;
        try { items = JSON.parse(el.textContent || '[]'); } catch (e) { return; }
        if (!items || !items.length) return;
        items.forEach(function (msg) {
            var tags = (msg.tags || '').toString();
            var icon = tags.indexOf('error') !== -1 ? 'error' : (tags.indexOf('warning') !== -1 ? 'warning' : 'success');
            var title = icon === 'error' ? 'Erreur' : (icon === 'warning' ? 'Attention' : 'Succès');
            window.Swal.fire({
                icon: icon,
                title: title,
                text: msg.text || '',
                confirmButtonColor: '#a83232'
            });
        });
    }

    function swapExtraCss(parsed) {
        var host = document.querySelector('[data-live-extra-css]');
        var next = parsed.querySelector('[data-live-extra-css]');
        if (host && next) host.innerHTML = next.innerHTML;
    }

    function swapNavbar(parsed) {
        var host = document.querySelector('[data-live-navbar]');
        var next = parsed.querySelector('[data-live-navbar]');
        if (host && next) host.innerHTML = next.innerHTML;
    }

    function hardNav(url) {
        window.location.href = url;
    }

    function applyDocument(html, url, opts) {
        opts = opts || {};
        var parsed = new DOMParser().parseFromString(html, 'text/html');
        var newRoot = parsed.querySelector('[data-live-filter-root]');
        var root = document.querySelector('[data-live-filter-root]');
        var newLayout = parsed.body ? (parsed.body.getAttribute('data-live-layout') || '') : '';
        var layout = currentLayout();
        if (!newRoot || !root || (layout && newLayout && layout !== newLayout)) {
            hardNav(url);
            return false;
        }
        if (parsed.getElementById('loginForm') && !document.getElementById('loginForm')) {
            hardNav(url);
            return false;
        }

        closeModals();
        destroyTables();
        destroyCharts(root);
        swapExtraCss(parsed);
        swapNavbar(parsed);
        root.innerHTML = newRoot.innerHTML;
        document.title = parsed.title || document.title;
        runScripts(root);
        runCustomJs(parsed);
        reinitTables();
        if (typeof window.pbInitLiveSearch === 'function') window.pbInitLiveSearch();
        if (typeof window.pbInitPeriodFilters === 'function') window.pbInitPeriodFilters();
        markSidebar(url);
        if (opts.showMessages !== false) showMessages(parsed);
        try {
            if (opts.push) window.history.pushState({ pbLive: 1 }, '', url);
            else window.history.replaceState({ pbLive: 1 }, '', url);
        } catch (e) {}
        document.dispatchEvent(new CustomEvent('pb:livepage', { detail: { url: url } }));
        document.dispatchEvent(new CustomEvent('pb:livefilter'));
        if (window.Alpine && typeof Alpine.initTree === 'function') {
            try { Alpine.initTree(root); } catch (e2) {}
        }
        return true;
    }

    function fetchPage(url, fetchOpts, applyOpts) {
        if (controller) controller.abort();
        controller = window.AbortController ? new AbortController() : null;
        setBusy(true);
        applying = true;

        var headers = Object.assign({
            'X-Requested-With': 'XMLHttpRequest',
            'X-PB-Live-Nav': '1'
        }, (fetchOpts && fetchOpts.headers) || {});
        var opts = {
            headers: headers,
            redirect: 'follow',
            credentials: 'same-origin'
        };
        if (fetchOpts && fetchOpts.method) opts.method = fetchOpts.method;
        if (fetchOpts && fetchOpts.body !== undefined) opts.body = fetchOpts.body;
        if (controller) opts.signal = controller.signal;

        return fetch(url.toString(), opts)
            .then(function (res) {
                var finalUrl = res.url || url.toString();
                var type = (res.headers.get('content-type') || '').toLowerCase();
                var disposition = (res.headers.get('content-disposition') || '').toLowerCase();
                if (disposition.indexOf('attachment') !== -1) {
                    hardNav(url.toString());
                    return null;
                }
                if (type.indexOf('application/json') !== -1) {
                    return res.json().then(function (data) {
                        return { json: data, url: finalUrl };
                    });
                }
                if (!res.ok) throw new Error('nav');
                return res.text().then(function (html) {
                    return { html: html, url: finalUrl };
                });
            })
            .then(function (payload) {
                if (!payload) return;
                if (payload.json) {
                    if (payload.json.success) {
                        return loadUrl(window.location.href, { push: false, showMessages: false }).then(function () {
                            if (window.Swal && payload.json.message) {
                                window.Swal.fire({
                                    icon: 'success',
                                    title: 'Succès',
                                    text: payload.json.message,
                                    confirmButtonColor: '#a83232'
                                });
                            }
                        });
                    }
                    if (payload.json.error || payload.json.errors) {
                        if (window.Swal) {
                            window.Swal.fire({
                                icon: 'error',
                                title: 'Erreur',
                                text: payload.json.error || 'Le formulaire contient des erreurs.',
                                confirmButtonColor: '#a83232'
                            });
                        }
                        return;
                    }
                    hardNav(url.toString());
                    return;
                }
                applyDocument(payload.html, payload.url, applyOpts);
            })
            .catch(function (err) {
                if (err && err.name === 'AbortError') return;
                hardNav(typeof url === 'string' ? url : url.toString());
            })
            .then(function () {
                setBusy(false);
                applying = false;
            });
    }

    function loadUrl(url, applyOpts) {
        applyOpts = applyOpts || {};
        var abs = new URL(url, window.location.origin);
        return fetchPage(abs, { headers: { 'X-PB-Live-Filter': '1' } }, applyOpts);
    }

    function isDownloadHref(href) {
        return /export|excel|download|csv|\.xlsx|\.xls|\.pdf|\.csv/i.test(href || '');
    }

    function isAuthHref(href) {
        return /log_out|\/logout\/?|\/login\/?/i.test(href || '');
    }

    function shouldLiveNav(anchor) {
        if (!anchor || !document.querySelector('[data-live-filter-root]')) return false;
        if (anchor.hasAttribute('data-no-live-nav') || anchor.hasAttribute('download')) return false;
        if (anchor.target && anchor.target !== '_self') return false;
        if (anchor.getAttribute('data-toggle') || anchor.getAttribute('data-widget')) return false;
        if (anchor.getAttribute('data-dismiss')) return false;
        var href = anchor.getAttribute('href');
        if (!href || href === '#' || href.indexOf('javascript:') === 0 || href.indexOf('mailto:') === 0) return false;
        if (isDownloadHref(href) || isAuthHref(href)) return false;
        try {
            var url = new URL(href, window.location.origin);
            if (url.origin !== window.location.origin) return false;
        } catch (e) {
            return false;
        }
        return true;
    }

    function patchReload() {
        if (window.pbReloadPatched) return;
        window.pbReloadPatched = true;
        var proto = window.Location && Location.prototype;
        if (!proto || !proto.reload) return;
        var nativeReload = proto.reload;
        proto.reload = function () {
            if (typeof window.pbRefreshLivePage === 'function' && document.querySelector('[data-live-filter-root]')) {
                window.pbRefreshLivePage();
                return;
            }
            return nativeReload.call(this);
        };
    }

    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form || form.tagName !== 'FORM') return;
        if (isFilterForm(form)) {
            e.preventDefault();
            loadUrl(formToUrl(form), { push: false });
            return;
        }
        if (isLivePostForm(form)) {
            e.preventDefault();
            var action = form.getAttribute('action') || window.location.href;
            fetchPage(new URL(action, window.location.origin), {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-PB-Live-Filter': '1' }
            }, { push: false });
        }
    });

    document.addEventListener('click', function (e) {
        var reset = e.target.closest('[data-live-filter-reset], a.pb-modal-default__btn-reset');
        if (reset) {
            var resetHref = reset.getAttribute('href');
            if (resetHref && resetHref !== '#') {
                e.preventDefault();
                loadUrl(new URL(resetHref, window.location.origin), { push: false });
                return;
            }
        }
        if (e.defaultPrevented) return;
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        var anchor = e.target.closest('a[href]');
        if (!shouldLiveNav(anchor)) return;
        e.preventDefault();
        var next = new URL(anchor.getAttribute('href'), window.location.origin);
        var same = next.pathname === window.location.pathname && next.search === window.location.search;
        loadUrl(next, { push: !same });
    });

    document.addEventListener('change', function (e) {
        if (e.target.id === 'period-select') {
            if (e.target.value === 'custom') return;
            var periodForm = e.target.closest('form');
            if (!isFilterForm(periodForm)) return;
            loadUrl(formToUrl(periodForm), { push: false });
            return;
        }
        var autoForm = e.target.closest('form.pb-panel__filter, form[data-live-filter-auto]');
        if (!autoForm || !isFilterForm(autoForm)) return;
        loadUrl(formToUrl(autoForm), { push: false });
    });

    window.addEventListener('popstate', function () {
        if (applying) return;
        loadUrl(window.location.href, { push: false, showMessages: false });
    });

    window.pbApplyLiveFilter = function (url) {
        return loadUrl(url, { push: false });
    };
    window.pbRefreshLivePage = function () {
        return loadUrl(window.location.href, { push: false, showMessages: false });
    };
    window.pbNavigateLive = function (url, push) {
        return loadUrl(url, { push: !!push });
    };
    window.pbMarkSidebar = markSidebar;

    patchReload();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            markSidebar(window.location.href);
        });
    } else {
        markSidebar(window.location.href);
    }
})();
