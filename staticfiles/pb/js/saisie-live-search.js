(function () {
    function debounce(fn, wait) {
        var timer;
        return function () {
            var ctx = this;
            var args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function () { fn.apply(ctx, args); }, wait);
        };
    }

    function initLiveSearch(form) {
        if (form.dataset.pbLiveBound === '1') return;
        form.dataset.pbLiveBound = '1';
        var input = form.querySelector('[data-live-input]');
        var results = document.querySelector(form.getAttribute('data-results') || '#pb-live-results');
        var countEl = document.querySelector(form.getAttribute('data-count') || '#pb-live-count');
        var clearBtn = form.querySelector('[data-live-clear]');
        var searchUrl = form.getAttribute('data-search-url') || window.location.pathname;
        if (!input || !results) return;

        var controller = null;

        function setLoading(on) {
            form.classList.toggle('is-loading', on);
            var spinner = form.querySelector('[data-live-spinner]');
            if (spinner) spinner.hidden = !on;
        }

        function syncClear() {
            if (clearBtn) clearBtn.hidden = !input.value.trim();
        }

        function updateHint(root) {
            if (!countEl) return;
            var hint = root && root.getAttribute('data-hint');
            if (hint) countEl.textContent = hint;
        }

        function syncUrl(query) {
            try {
                var url = new URL(window.location.href);
                if (query) url.searchParams.set('search', query);
                else url.searchParams.delete('search');
                url.searchParams.delete('partial');
                window.history.replaceState({}, '', url.pathname + url.search);
            } catch (e) {}
        }

        function fetchResults(query) {
            if (controller) controller.abort();
            controller = window.AbortController ? new AbortController() : null;
            setLoading(true);

            var url = new URL(searchUrl, window.location.origin);
            var current = new URL(window.location.href);
            current.searchParams.forEach(function (value, key) {
                if (key !== 'search' && key !== 'partial') url.searchParams.set(key, value);
            });
            if (query) url.searchParams.set('search', query);
            url.searchParams.set('partial', '1');

            var opts = { headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-PB-Live-Search': '1' } };
            if (controller) opts.signal = controller.signal;

            fetch(url.toString(), opts)
                .then(function (res) {
                    if (!res.ok) throw new Error('search');
                    return res.text();
                })
                .then(function (html) {
                    results.innerHTML = html;
                    updateHint(results.querySelector('[data-hint]') || results.firstElementChild);
                    syncUrl(query);
                })
                .catch(function (err) {
                    if (err && err.name === 'AbortError') return;
                })
                .then(function () {
                    setLoading(false);
                    syncClear();
                });
        }

        var run = debounce(function () {
            fetchResults(input.value.trim());
        }, 280);

        input.addEventListener('input', function () {
            syncClear();
            run();
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            fetchResults(input.value.trim());
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', function () {
                input.value = '';
                syncClear();
                input.focus();
                fetchResults('');
            });
        }

        syncClear();
        updateHint(results.querySelector('[data-hint]') || results.firstElementChild);
    }

    function initTableFilter(form) {
        if (form.dataset.pbLiveBound === '1') return;
        form.dataset.pbLiveBound = '1';
        var input = form.querySelector('[data-live-input]');
        var table = document.querySelector(form.getAttribute('data-live-table'));
        var countEl = document.querySelector(form.getAttribute('data-count'));
        var clearBtn = form.querySelector('[data-live-clear]');
        if (!input || !table) return;

        var rows = table.querySelectorAll('tbody tr');

        function syncClear() {
            if (clearBtn) clearBtn.hidden = !input.value.trim();
        }

        function applyFilter() {
            var query = input.value.trim().toLowerCase();
            var visible = 0;
            rows.forEach(function (row) {
                var match = !query || (row.textContent || '').toLowerCase().indexOf(query) !== -1;
                row.style.display = match ? '' : 'none';
                if (match) visible += 1;
            });
            if (countEl) {
                countEl.textContent = query
                    ? visible + ' résultat' + (visible > 1 ? 's' : '')
                    : rows.length + ' ligne' + (rows.length > 1 ? 's' : '');
            }
            syncClear();
        }

        var run = debounce(applyFilter, 120);
        input.addEventListener('input', run);
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            applyFilter();
        });
        if (clearBtn) {
            clearBtn.addEventListener('click', function () {
                input.value = '';
                applyFilter();
                input.focus();
            });
        }
        applyFilter();
    }

    function initAll() {
        document.querySelectorAll('[data-live-search]').forEach(function (form) {
            if (form.getAttribute('data-live-table')) initTableFilter(form);
            else initLiveSearch(form);
        });
    }

    window.pbInitLiveSearch = initAll;
    initAll();
})();
