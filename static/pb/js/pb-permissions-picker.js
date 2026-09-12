(function () {
    if (window.pbPermissionsPickerBound) return;
    window.pbPermissionsPickerBound = true;

    function normalize(value) {
        return String(value || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim();
    }

    function filterPicker(picker) {
        if (!picker) return;
        var input = picker.querySelector('.js-permission-search');
        var clearBtn = picker.querySelector('.js-permission-clear');
        var emptyEl = picker.querySelector('.js-permission-empty');
        var query = normalize(input && input.value);
        var visible = 0;

        picker.querySelectorAll('.js-permission-item').forEach(function (item) {
            var haystack = normalize(
                item.getAttribute('data-permission-text') || item.textContent
            );
            var match = !query || haystack.indexOf(query) !== -1;
            item.classList.toggle('is-filtered-out', !match);
            if (match) visible += 1;
        });

        picker.querySelectorAll('[data-permission-group]').forEach(function (group) {
            var hasVisible = !!group.querySelector('.js-permission-item:not(.is-filtered-out)');
            group.classList.toggle('is-filtered-out', !hasVisible);
        });

        if (clearBtn) {
            if (query) clearBtn.removeAttribute('hidden');
            else clearBtn.setAttribute('hidden', '');
        }
        if (emptyEl) {
            if (query && visible === 0) emptyEl.removeAttribute('hidden');
            else emptyEl.setAttribute('hidden', '');
        }
    }

    function pickerFrom(el) {
        return el && el.closest ? el.closest('[data-permission-picker]') : null;
    }

    function resetPicker(picker) {
        var input = picker && picker.querySelector('.js-permission-search');
        if (input) input.value = '';
        filterPicker(picker);
    }

    document.addEventListener('input', function (e) {
        var input = e.target.closest && e.target.closest('.js-permission-search');
        if (!input) return;
        filterPicker(pickerFrom(input));
    });

    document.addEventListener('search', function (e) {
        var input = e.target.closest && e.target.closest('.js-permission-search');
        if (!input) return;
        filterPicker(pickerFrom(input));
    });

    document.addEventListener('click', function (e) {
        var btn = e.target.closest && e.target.closest('.js-permission-clear');
        if (!btn) return;
        var picker = pickerFrom(btn);
        var input = picker && picker.querySelector('.js-permission-search');
        if (!input) return;
        input.value = '';
        filterPicker(picker);
        input.focus();
    });

    document.addEventListener('keydown', function (e) {
        var modal = document.querySelector('.modal.show');
        var picker = modal
            ? modal.querySelector('[data-permission-picker]')
            : (e.target.closest && e.target.closest('[data-permission-picker]'));
        if (!picker) return;

        if ((e.ctrlKey || e.metaKey) && (e.key === 'f' || e.key === 'F')) {
            e.preventDefault();
            var focusInput = picker.querySelector('.js-permission-search');
            if (focusInput) focusInput.focus();
            return;
        }

        if (e.key === 'Enter' && e.target.classList && e.target.classList.contains('js-permission-search')) {
            e.preventDefault();
            return;
        }

        if (e.key === 'Escape' && e.target.classList && e.target.classList.contains('js-permission-search')) {
            if (e.target.value) {
                e.preventDefault();
                e.stopPropagation();
                e.target.value = '';
                filterPicker(picker);
            }
        }
    }, true);

    var $ = window.jQuery || window.$;
    if ($) {
        $(document).on('hidden.bs.modal', '.modal', function () {
            var picker = this.querySelector('[data-permission-picker]');
            if (picker) resetPicker(picker);
        });
        $(document).on('shown.bs.modal', '.modal', function () {
            var picker = this.querySelector('[data-permission-picker]');
            if (picker) filterPicker(picker);
        });
    }
})();
