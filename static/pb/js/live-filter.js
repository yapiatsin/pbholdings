(function () {
    var controller = null;

    function isPost(form) {
        return (form.getAttribute('method') || 'get').toLowerCase() === 'post';
    }

    function isFilterForm(form) {
        if (!form || form.tagName !== 'FORM' || isPost(form)) return false;
        if (form.hasAttribute('data-no-live-filter')) return false;
        if (form.hasAttribute('data-live-search')) return false;
        if (form.classList.contains('pb-navbar-search-form')) return false;
        if (form.id === 'motifSortiForm') return false;
        if (form.hasAttribute('data-live-filter')) return true;
        if (form.id === 'basic-form') return true;
        if (form.classList.contains('pb-panel__filter')) return true;
        if (form.classList.contains('search-form')) return true;
        return !!(form.querySelector('[name="date_debut"], [name="periode"], [name="categorie"], [name="immatriculation"]'));
    }

    function closeModals() {
        if (window.jQuery) {
            window.jQuery('.modal').modal('hide');
            window.jQuery('.modal-backdrop').remove();
            window.jQuery('body').removeClass('modal-open').css('padding-right', '');
        }
    }

    function setBusy(on) {
        document.body.classList.toggle('pb-live-filter-busy', on);
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

    function shouldRunScript(script) {
        var src = script.getAttribute('src') || '';
        if (src.indexOf('saisie-live-search.js') !== -1) return false;
        if (src.indexOf('live-filter.js') !== -1) return false;
        var code = script.textContent || '';
        if (!code.trim() && !src) return false;
        if (/\$\(\s*document\s*\)\.on/.test(code)) return false;
        return true;
    }

    function runScripts(scope) {
        if (!scope) return;
        scope.querySelectorAll('script').forEach(function (old) {
            if (!shouldRunScript(old)) return;
            var neu = document.createElement('script');
            Array.prototype.forEach.call(old.attributes, function (attr) {
                neu.setAttribute(attr.name, attr.value);
            });
            neu.textContent = old.textContent;
            old.parentNode.replaceChild(neu, old);
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

    function applyUrl(url) {
        if (controller) controller.abort();
        controller = window.AbortController ? new AbortController() : null;
        setBusy(true);

        var opts = { headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-PB-Live-Filter': '1' } };
        if (controller) opts.signal = controller.signal;

        return fetch(url.toString(), opts)
            .then(function (res) {
                if (!res.ok) throw new Error('filter');
                return res.text();
            })
            .then(function (html) {
                var parsed = new DOMParser().parseFromString(html, 'text/html');
                var newRoot = parsed.querySelector('[data-live-filter-root]');
                var root = document.querySelector('[data-live-filter-root]');
                if (!newRoot || !root) {
                    window.location.href = url.toString();
                    return;
                }
                closeModals();
                destroyTables();
                destroyCharts(root);
                root.innerHTML = newRoot.innerHTML;
                runScripts(root);
                reinitTables();
                if (typeof window.pbInitLiveSearch === 'function') window.pbInitLiveSearch();
                if (typeof window.pbInitPeriodFilters === 'function') window.pbInitPeriodFilters();
                try { window.history.replaceState({}, '', url.pathname + url.search); } catch (e) {}
                document.dispatchEvent(new CustomEvent('pb:livefilter'));
            })
            .catch(function (err) {
                if (err && err.name === 'AbortError') return;
                window.location.href = url.toString();
            })
            .then(function () {
                setBusy(false);
            });
    }

    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!isFilterForm(form)) return;
        e.preventDefault();
        applyUrl(formToUrl(form));
    });

    document.addEventListener('click', function (e) {
        var reset = e.target.closest('[data-live-filter-reset], a.pb-modal-default__btn-reset');
        if (!reset) return;
        var href = reset.getAttribute('href');
        if (!href || href === '#') return;
        e.preventDefault();
        applyUrl(new URL(href, window.location.origin));
    });

    document.addEventListener('change', function (e) {
        if (e.target.id === 'period-select') {
            if (e.target.value === 'custom') return;
            var periodForm = e.target.closest('form');
            if (!isFilterForm(periodForm)) return;
            applyUrl(formToUrl(periodForm));
            return;
        }
        var autoForm = e.target.closest('form.pb-panel__filter, form[data-live-filter-auto]');
        if (!autoForm || !isFilterForm(autoForm)) return;
        applyUrl(formToUrl(autoForm));
    });

    window.pbApplyLiveFilter = applyUrl;
})();
