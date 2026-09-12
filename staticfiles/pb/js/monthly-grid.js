(function () {
    if (window.pbMonthlyGridBound) return;
    window.pbMonthlyGridBound = true;

    var controller = null;
    var partsByImmat = {};

    function $(id) {
        return document.getElementById(id);
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function formatAmount(value) {
        var n = Math.round(Number(value) || 0);
        var sign = n < 0 ? '-' : '';
        return sign + String(Math.abs(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function numClass(value) {
        return Number(value) ? 'text-danger' : 'text-cyan';
    }

    function motifPills(obj, keys) {
        obj = obj || {};
        return keys.map(function (key) {
            var n = Number(obj[key]) || 0;
            return '<span class="temparret-mini">' + escapeHtml(key) + ' ' + n + '</span>';
        }).join('');
    }

    function setLoading(wrap, on) {
        if (!wrap) return;
        wrap.classList.toggle('is-loading', !!on);
    }

    function currentFilters() {
        var monthEl = $('month');
        var yearEl = $('year');
        var catEl = $('categorie');
        return {
            month: monthEl ? monthEl.value : '',
            year: yearEl ? yearEl.value : '',
            categorie: catEl ? catEl.value : ''
        };
    }

    function dataQuery(filters) {
        var params = new URLSearchParams();
        params.set('format', 'json');
        if (filters.month) params.set('month', filters.month);
        if (filters.year) params.set('year', filters.year);
        if (filters.categorie) params.set('categorie', filters.categorie);
        return params.toString();
    }

    function pageQuery(filters) {
        var params = new URLSearchParams();
        if (filters.month) params.set('month', filters.month);
        if (filters.year) params.set('year', filters.year);
        if (filters.categorie) params.set('categorie', filters.categorie);
        return params.toString();
    }

    function fetchGrid() {
        var kind = $('temp-arret-table') ? 'temps' : ($('myrecette-table') ? 'recette' : null);
        if (!kind) return;
        var filters = currentFilters();
        var wrap = document.querySelector('.myrecette-table-scroll');
        setLoading(wrap, true);
        if (controller) controller.abort();
        controller = window.AbortController ? new AbortController() : null;
        fetch('?' + dataQuery(filters), {
            headers: {
                'Accept': 'application/json',
                'X-PB-Grid': 'json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            signal: controller ? controller.signal : undefined
        })
            .then(function (res) {
                if (!res.ok) throw new Error('grid');
                return res.json();
            })
            .then(function (data) {
                if (kind === 'temps') renderTemps(data);
                else renderRecette(data);
                var qs = pageQuery(filters);
                if (window.history && window.history.replaceState) {
                    window.history.replaceState({}, '', qs ? ('?' + qs) : window.location.pathname);
                }
            })
            .catch(function (err) {
                if (err && err.name === 'AbortError') return;
                var tbody = document.querySelector('#temp-arret-table tbody, #myrecette-table tbody');
                if (tbody) {
                    tbody.innerHTML = '<tr><td class="pb-empty" colspan="40">Impossible de charger les données.</td></tr>';
                }
            })
            .then(function () {
                setLoading(wrap, false);
            });
    }

    function updateTable(month, year) {
        var monthEl = $('month');
        var yearEl = $('year');
        if (monthEl && month != null) monthEl.value = String(month);
        if (yearEl && year != null) yearEl.value = String(year);
        fetchGrid();
    }

    function changeMonth(offset) {
        var monthEl = $('month');
        var yearEl = $('year');
        if (!monthEl || !yearEl) return;
        var month = parseInt(monthEl.value, 10);
        var year = parseInt(yearEl.value, 10);
        if (!month || !year) return;
        month += offset;
        if (month > 12) { month = 1; year += 1; }
        else if (month < 1) { month = 12; year -= 1; }
        if (![].some.call(yearEl.options, function (opt) { return String(opt.value) === String(year); })) {
            var opt = document.createElement('option');
            opt.value = year;
            opt.textContent = year;
            yearEl.appendChild(opt);
        }
        monthEl.value = String(month);
        yearEl.value = String(year);
        fetchGrid();
    }

    function selectMonthYear() {
        fetchGrid();
    }

    function bindMonthNav() {
        window.updateTable = updateTable;
        window.changeMonth = changeMonth;
        window.selectMonthYear = selectMonthYear;
    }

    function renderTemps(data) {
        var table = $('temp-arret-table');
        if (!table) return;
        var days = data.days || [];
        var vehicles = data.vehicles || [];
        var totals = data.totals || {};
        var hint = $('temparret-period-hint');
        if (hint) hint.textContent = (data.month_name || '') + ' ' + (data.year || '');
        partsByImmat = {};

        var dayHeads = days.map(function (day) {
            return '<th class="pb-table__num">' + day + '</th>';
        }).join('');
        table.querySelector('thead').innerHTML =
            '<tr>' +
                '<th rowspan="2">Immat</th>' +
                '<th rowspan="2">Marque</th>' +
                '<th colspan="' + days.length + '">' +
                    '<button type="button" class="btn btn-default btn-prev" data-month-offset="-1" aria-label="Mois précédent"><i class="fa fa-angle-double-left" aria-hidden="true"></i></button> ' +
                    escapeHtml(data.month_name) + ' - ' + escapeHtml(data.year) +
                    ' <button type="button" class="btn btn-default btn-next" data-month-offset="1" aria-label="Mois suivant"><i class="fa fa-angle-double-right" aria-hidden="true"></i></button>' +
                '</th>' +
                '<th rowspan="2" class="pb-table__num">T arrêt</th>' +
                '<th rowspan="2" class="pb-table__num">T Pièce</th>' +
                '<th rowspan="2" class="pb-table__num">Recette</th>' +
                '<th rowspan="2">Pièce</th>' +
                '<th rowspan="2">Motif rép</th>' +
                '<th rowspan="2">Motif arrêt</th>' +
            '</tr>' +
            '<tr>' + dayHeads + '</tr>';

        var tbody;
        if (!vehicles.length) {
            tbody = '<tr><td colspan="' + (days.length + 8) + '" class="pb-empty">Aucun véhicule pour cette sélection.</td></tr>';
        } else {
            tbody = vehicles.map(function (row) {
                partsByImmat[row.immatriculation] = row.part_details || [];
                var daysHtml = (row.daily_actions || []).map(function (value) {
                    return '<td class="pb-table__num ' + numClass(value) + '">' + formatAmount(value) + '</td>';
                }).join('');
                var partsBtn = (row.part_details && row.part_details.length)
                    ? '<button type="button" class="pb-table__action js-open-parts" data-immat="' + escapeHtml(row.immatriculation) + '" title="Détail des pièces — ' + escapeHtml(row.immatriculation) + '"><i class="fas fa-file-alt" aria-hidden="true"></i></button>'
                    : '<span class="text-muted">—</span>';
                return '<tr>' +
                    '<td><a href="#" title="' + escapeHtml(row.category) + '"><span class="pb-table__key">' + escapeHtml(row.immatriculation) + '</span></a></td>' +
                    '<td class="pb-table__muted">' + escapeHtml(row.marque) + '</td>' +
                    daysHtml +
                    '<td class="pb-table__num text-warning">' + formatAmount(row.total_actions) + '</td>' +
                    '<td class="pb-table__num">' + formatAmount(row.total_cost_parts) + '</td>' +
                    '<td class="pb-table__num">' + formatAmount(row.total_income) + '</td>' +
                    '<td class="text-center">' + partsBtn + '</td>' +
                    '<td>' + motifPills(row.repairs_by_motif, ['P-vis', 'pan', 'acc']) + '</td>' +
                    '<td>' + motifPills(row.motif_arret, ['vis', 'ent', 'aut']) + '</td>' +
                    '</tr>';
            }).join('');
        }
        table.querySelector('tbody').innerHTML = tbody;

        var tfoot = table.querySelector('tfoot');
        if (!tfoot) {
            tfoot = document.createElement('tfoot');
            table.appendChild(tfoot);
        }
        var dayTotals = (data.daily_totals || []).map(function (value) {
            return '<th class="pb-table__num text-danger">' + formatAmount(value) + '</th>';
        }).join('');
        tfoot.innerHTML =
            '<tr>' +
                '<th colspan="2" class="pb-table__num">Total par jour :</th>' +
                dayTotals +
                '<th class="pb-table__num text-danger">' + formatAmount(totals.actions) + '</th>' +
                '<th class="pb-table__num text-danger">' + formatAmount(totals.cost_parts) + '</th>' +
                '<th class="pb-table__num text-danger">' + formatAmount(totals.income) + '</th>' +
                '<th class="pb-table__num text-danger">' + formatAmount(totals.pieces) + '</th>' +
                '<th class="text-danger">' + formatAmount(totals.repairs_by_motif) + '</th>' +
                '<th class="text-danger">' + formatAmount(totals.motif_arrets) + '</th>' +
            '</tr>';

        var legend = $('temparret-legend');
        if (legend) {
            var map = {
                visit: totals.visit,
                panne: totals.panne,
                accident: totals.accident,
                autrarret: totals.autrarret,
                visitech: totals.visite_technique,
                entretien: totals.entretien
            };
            ['visit', 'panne', 'accident', 'autrarret', 'visitech', 'entretien'].forEach(function (key) {
                var el = legend.querySelector('[data-legend="' + key + '"]');
                if (el) el.textContent = formatAmount(map[key]);
            });
        }
    }

    function renderRecette(data) {
        var table = $('myrecette-table');
        if (!table) return;
        var days = data.days || [];
        var vehicles = data.vehicles || [];
        var totals = data.totals || {};
        var hint = $('myrecette-period-hint');
        if (hint) hint.textContent = (data.month_name || '') + ' ' + (data.year || '');

        var dayHeads = days.map(function (day) {
            return '<th style="font-size:12px" class="text-primary">' + day + '</th>';
        }).join('');
        table.querySelector('thead').innerHTML =
            '<tr class="text-danger">' +
                '<th rowspan="2">Immat</th>' +
                '<th rowspan="2">Marque</th>' +
                '<th colspan="' + days.length + '">' +
                    '<button type="button" class="btn btn-default btn-prev" data-month-offset="-1" aria-label="Mois précédent"><i class="fa fa-angle-double-left" aria-hidden="true"></i></button> ' +
                    escapeHtml(data.month_name) + ' - ' + escapeHtml(data.year) +
                    ' <button type="button" class="btn btn-default btn-next" data-month-offset="1" aria-label="Mois suivant"><i class="fa fa-angle-double-right" aria-hidden="true"></i></button>' +
                '</th>' +
                '<th rowspan="2">Aujourd\'hui</th>' +
                '<th rowspan="2">A verser</th>' +
                '<th rowspan="2">Ecart</th>' +
                '<th rowspan="2">T Recette</th>' +
                '<th rowspan="2">A payer</th>' +
                '<th rowspan="2">Motif du jour</th>' +
            '</tr>' +
            '<tr>' + dayHeads + '</tr>';

        var tbody;
        if (!vehicles.length) {
            tbody = '<tr><td colspan="' + (days.length + 8) + '" class="pb-empty">Aucun véhicule pour cette sélection.</td></tr>';
        } else {
            tbody = vehicles.map(function (row) {
                var daysHtml = (row.daily_actions || []).map(function (value) {
                    return '<td class="' + numClass(value) + '">' + formatAmount(value) + '</td>';
                }).join('');
                return '<tr>' +
                    '<td><a href="#" title="' + escapeHtml(row.category) + '"><span class="pb-table__key">' + escapeHtml(row.immatriculation) + '</span></a></td>' +
                    '<td>' + escapeHtml(row.marque) + '</td>' +
                    daysHtml +
                    '<td class="text-warning">' + formatAmount(row.recette_versee) + '</td>' +
                    '<td>' + formatAmount(row.recette_attendue) + '</td>' +
                    '<td>' + formatAmount(row.difference) + '</td>' +
                    '<td>' + formatAmount(row.recette_mensuelle) + '</td>' +
                    '<td>' + formatAmount(row.difference_mensuelle) + '</td>' +
                    '<td>' + motifPills(row.motif_arrets, ['vis', 'ent', 'rep']) + '</td>' +
                    '</tr>';
            }).join('');
        }
        table.querySelector('tbody').innerHTML = tbody;

        var dayTotals = (data.daily_totals || []).map(function (value) {
            return '<td class="text-danger myrecette-total-day">' + formatAmount(value) + '</td>';
        }).join('');
        table.querySelector('tfoot').innerHTML =
            '<tr>' +
                '<td colspan="2" class="pb-table__num">Total par jour :</td>' +
                dayTotals +
                '<td class="text-danger">' + formatAmount(totals.today) + '</td>' +
                '<td class="text-danger">' + formatAmount(totals.a_verser) + '</td>' +
                '<td class="text-danger">' + formatAmount(totals.ecart) + '</td>' +
                '<td class="text-danger">' + formatAmount(totals.recette_mois) + '</td>' +
                '<td class="text-danger">' + formatAmount(totals.a_payer) + '</td>' +
                '<td class="text-danger">' + formatAmount(totals.motifs) + '</td>' +
            '</tr>';

        var recap = $('myrecette-recap');
        if (recap) {
            var items = data.recap || [];
            if (!items.length) {
                recap.innerHTML = '';
                recap.hidden = true;
            } else {
                recap.hidden = false;
                recap.innerHTML = '<h3 class="temparret-legend__heading">Récapitulatif par catégorie</h3><div class="temparret-legend__chips">' +
                    items.map(function (cat) {
                        return '<article class="temparret-legend__chip temparret-legend__chip--primary">' +
                            '<span class="temparret-legend__dot" aria-hidden="true"></span>' +
                            '<span class="temparret-legend__meta">' +
                                '<span class="temparret-legend__code">' + escapeHtml(cat.nb_vehicules) + ' véh.</span>' +
                                '<span class="temparret-legend__label">' + escapeHtml(cat.categorie) + '</span>' +
                            '</span>' +
                            '<span class="temparret-legend__value">' + formatAmount(cat.recette_attendue) + '</span>' +
                            '</article>';
                    }).join('') + '</div>';
            }
        }
    }

    function bindFilters() {
        var bar = $('temparret-filterbar') || $('myrecette-filterbar');
        if (bar && !bar.dataset.gridBound) {
            bar.dataset.gridBound = '1';
            bar.addEventListener('change', function (event) {
                if (event.target && event.target.matches('select')) fetchGrid();
            });
        }
        var exportBtn = $('export-excel-btn');
        if (exportBtn && !exportBtn.dataset.gridBound) {
            exportBtn.dataset.gridBound = '1';
            exportBtn.addEventListener('click', function (e) {
                e.preventDefault();
                var baseUrl = exportBtn.getAttribute('data-export-url');
                window.location.href = baseUrl + '?' + pageQuery(currentFilters());
            });
        }
    }

    function renderPartsModal(immat, parts) {
        var immatEl = $('modal-pieces-immat');
        var bodyEl = $('modal-pieces-body');
        if (immatEl) immatEl.textContent = immat || '';
        if (!bodyEl) return;
        if (!parts.length) {
            bodyEl.innerHTML = '<tr><td colspan="3"><p class="pb-empty mb-0">Aucune pièce sur cette période.</p></td></tr>';
            return;
        }
        var totalQty = 0;
        var totalAmount = 0;
        var rows = parts.map(function (part) {
            var qty = Number(part.count) || 0;
            var amount = Number(part.total_price) || 0;
            totalQty += qty;
            totalAmount += amount;
            return '<tr><td class="pb-table__key">' + escapeHtml(part.libelle) + '</td>' +
                '<td class="pb-table__num">' + qty + '</td>' +
                '<td class="pb-table__num">' + formatAmount(amount) + '</td></tr>';
        });
        rows.push(
            '<tr><th>Total</th><th class="pb-table__num">' + totalQty +
            '</th><th class="pb-table__num">' + formatAmount(totalAmount) + '</th></tr>'
        );
        bodyEl.innerHTML = rows.join('');
    }

    document.addEventListener('click', function (event) {
        var nav = event.target.closest && event.target.closest('[data-month-offset]');
        if (nav) {
            event.preventDefault();
            changeMonth(parseInt(nav.getAttribute('data-month-offset'), 10) || 0);
            return;
        }
        var btn = event.target.closest && event.target.closest('.js-open-parts');
        if (!btn) return;
        event.preventDefault();
        var immat = btn.getAttribute('data-immat') || '';
        renderPartsModal(immat, partsByImmat[immat] || []);
        if (window.jQuery) window.jQuery('#modal-pieces').modal('show');
    });

    function boot() {
        bindMonthNav();
        if (!$('temp-arret-table') && !$('myrecette-table')) return;
        bindFilters();
        fetchGrid();
    }

    document.addEventListener('pb:livepage', boot);
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
