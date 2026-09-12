(function () {
    if (window.pbLiveTableActionsBound) return;
    window.pbLiveTableActionsBound = true;

    function jq() {
        return window.jQuery || window.$;
    }

    function csrfToken() {
        var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input && input.value) return input.value;
        var match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    function toast(kind, title) {
        if (!window.Swal) return;
        var Mixin = window.Swal.mixin({
            toast: true,
            position: 'top',
            showConfirmButton: false,
            timer: 4000,
            timerProgressBar: true
        });
        Mixin.fire({ type: kind, icon: kind, title: title });
    }

    function refreshPage() {
        if (typeof window.pbRefreshLivePage === 'function') {
            window.pbRefreshLivePage();
            return;
        }
        window.location.reload();
    }

    function openAjaxModal(trigger, modalId, bodyId) {
        var $ = jq();
        if (!$ || !trigger) return;
        var url = trigger.getAttribute('data-url');
        if (!url) return;
        $.get(url, function (data) {
            $(bodyId).html(data);
            $(modalId).modal('show');
        });
    }

    function ajaxUpdateForm(form, modalId, bodyId) {
        var $ = jq();
        if (!$ || !form) return;
        $.post(form.getAttribute('action') || window.location.href, $(form).serialize(), function (data) {
            if (data && data.success) {
                $(modalId).modal('hide');
                toast('success', data.message);
                setTimeout(refreshPage, 400);
            } else {
                $(bodyId).html(data);
            }
        });
    }

    function spinnerHtml() {
        return '<div class="text-center"><div class="spinner-border" role="status"><span class="sr-only">Chargement...</span></div></div>';
    }

    function loadAccountJsonModal(trigger, titleId, titlePrefix, bodyId) {
        var $ = jq();
        if (!$ || !trigger) return;
        var url = trigger.getAttribute('data-url');
        var username = trigger.getAttribute('data-username') || '';
        var title = document.querySelector(titleId);
        if (title) {
            var icon = title.querySelector('img');
            title.textContent = titlePrefix + username;
            if (icon) title.insertBefore(icon, title.firstChild);
        }
        $(bodyId).html(spinnerHtml());
        $.ajax({
            url: url,
            type: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (r) {
                $(bodyId).html((r && r.html) || '<div class="alert alert-danger">Erreur.</div>');
            },
            error: function (xhr) {
                var html = xhr.responseJSON && xhr.responseJSON.html;
                $(bodyId).html(html || '<div class="alert alert-danger">Erreur de chargement.</div>');
            }
        });
    }

    function submitAccountModalForm(form) {
        var $ = jq();
        if (!$ || !form) return;
        var btn = form.querySelector('button[type=submit]');
        var orig = btn ? btn.innerHTML : '';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Enregistrement...';
        }
        var isPerm = form.id === 'permission-form-modal';
        var modalId = isPerm ? '#permissionModal' : '#editAccountModal';
        var bodyId = isPerm ? '#permission-modal-body' : '#edit-account-modal-body';
        var failText = isPerm ? 'Erreur permissions.' : 'Erreur mise à jour.';
        $.ajax({
            url: form.getAttribute('action'),
            type: 'POST',
            data: $(form).serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (r) {
                if (r && r.success) {
                    $(modalId).modal('hide');
                    refreshPage();
                    return;
                }
                if (window.Swal) {
                    window.Swal.fire({ icon: 'error', title: 'Erreur', text: (r && r.message) || failText });
                }
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = orig;
                }
            },
            error: function (xhr) {
                if (xhr.responseJSON && xhr.responseJSON.html) {
                    $(bodyId).html(xhr.responseJSON.html);
                } else if (window.Swal) {
                    window.Swal.fire({ icon: 'error', title: 'Erreur', text: failText });
                }
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = orig;
                }
            }
        });
    }

    function syncGerantSection(select) {
        if (!select) return;
        var isGerant = select.value === '4';
        var root = select.closest('form') || document;
        var section = root.querySelector('#gerant-voiture-section, #edit-gerant-voiture-section');
        if (!section) return;
        section.style.display = isGerant ? '' : 'none';
        if (!isGerant) {
            section.querySelectorAll('input[type=checkbox]').forEach(function (cb) {
                cb.checked = false;
            });
        }
    }

    function syncAllGerantSections() {
        document.querySelectorAll('select[name="user_type"]').forEach(syncGerantSection);
    }

    document.addEventListener('click', function (e) {
        var master = e.target.closest('#checkAll');
        if (master && master.type === 'checkbox') {
            var form = master.closest('form');
            if (!form) return;
            form.querySelectorAll('tbody input[type="checkbox"][name]').forEach(function (cb) {
                cb.checked = master.checked;
            });
            return;
        }

        var editVeh = e.target.closest('.edit-vehicule-btn');
        if (editVeh) {
            e.preventDefault();
            openAjaxModal(editVeh, '#editCarModal', '#modalBodyContent');
            return;
        }

        var editCat = e.target.closest('.edit-categorie-btn');
        if (editCat) {
            e.preventDefault();
            openAjaxModal(editCat, '#editcategorieModal', '#modalBodyContent');
            return;
        }

        var editPerm = e.target.closest('.edit-permissions-btn');
        if (editPerm) {
            e.preventDefault();
            loadAccountJsonModal(editPerm, '#permissionModalLabel', 'Modifier les permissions — ', '#permission-modal-body');
            return;
        }

        var editAcc = e.target.closest('.edit-account-btn');
        if (editAcc) {
            e.preventDefault();
            loadAccountJsonModal(editAcc, '#editAccountModalLabel', 'Modifier — ', '#edit-account-modal-body');
        }
    });

    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form || form.tagName !== 'FORM') return;

        if (form.id === 'CarUpdateForm') {
            e.preventDefault();
            ajaxUpdateForm(form, '#editCarModal', '#modalBodyContent');
            return;
        }

        if (form.id === 'categorieUpdateForm') {
            e.preventDefault();
            ajaxUpdateForm(form, '#editcategorieModal', '#modalBodyContent');
            return;
        }

        if (form.id === 'permission-form-modal' || form.id === 'account-edit-form-modal') {
            e.preventDefault();
            submitAccountModalForm(form);
            return;
        }

        if (form.id === 'motifSortiForm') {
            e.preventDefault();
            var $ = jq();
            if (!$) return;
            var motifEl = document.getElementById('motif_sorti_input');
            var motif = motifEl ? motifEl.value.trim() : '';
            if (!motif) {
                alert('Veuillez saisir un motif de sortie.');
                return;
            }
            var checkbox = window.pbCurrentCarStatut;
            if (!checkbox) return;
            $.ajax({
                url: checkbox.getAttribute('data-url'),
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: csrfToken(),
                    motif_sorti: motif
                },
                success: function (response) {
                    if (response && response.success) {
                        $('#motifSortiModal').modal('hide');
                        checkbox.checked = false;
                        window.pbCurrentCarStatut = null;
                        toast('error', 'Véhicule retiré du stock avec succès !');
                    } else {
                        alert((response && response.error) || 'Erreur lors de la mise à jour.');
                        checkbox.checked = true;
                    }
                },
                error: function () {
                    alert('Erreur lors de la mise à jour du statut.');
                    checkbox.checked = true;
                }
            });
        }
    });

    document.addEventListener('change', function (e) {
        var userType = e.target.closest('select[name="user_type"]');
        if (userType) {
            syncGerantSection(userType);
            return;
        }

        var activeToggle = e.target.closest('.toggle-active');
        if (activeToggle) {
            var $ = jq();
            if (!$) return;
            $.ajax({
                url: activeToggle.getAttribute('data-url'),
                type: 'POST',
                data: { csrfmiddlewaretoken: csrfToken() },
                success: function (response) {
                    if (response && response.success) {
                        toast(
                            response.is_active ? 'success' : 'error',
                            response.is_active ? 'Compte activé avec succès.' : 'Compte désactivé avec succès.'
                        );
                    }
                },
                error: function () {
                    activeToggle.checked = !activeToggle.checked;
                    alert('Erreur lors de la mise à jour du compte.');
                }
            });
        }
    });

    document.addEventListener('change', function (e) {
        var checkbox = e.target.closest('.toggle-car-statut');
        if (!checkbox) return;
        var $ = jq();
        if (!$) return;
        var url = checkbox.getAttribute('data-url');
        var vehiculeId = checkbox.getAttribute('data-vehicule-id');
        if (checkbox.checked) {
            $.ajax({
                url: url,
                type: 'POST',
                data: { csrfmiddlewaretoken: csrfToken() },
                success: function (response) {
                    if (response && response.success) {
                        toast('success', 'Véhicule réintégré dans le stock avec succès !');
                    }
                },
                error: function () {
                    checkbox.checked = false;
                    alert('Erreur lors de la mise à jour du statut.');
                }
            });
            return;
        }
        window.pbCurrentCarStatut = checkbox;
        var hidden = document.getElementById('vehicule_id_hidden');
        var motif = document.getElementById('motif_sorti_input');
        if (hidden) hidden.value = vehiculeId || '';
        if (motif) motif.value = '';
        $('#motifSortiModal').modal('show');
        checkbox.checked = true;
    });

    var $ready = jq();
    if ($ready) {
        $ready(document).on('hidden.bs.modal', '#motifSortiModal', function () {
            if (window.pbCurrentCarStatut) {
                window.pbCurrentCarStatut.checked = true;
                window.pbCurrentCarStatut = null;
            }
            var motif = document.getElementById('motif_sorti_input');
            if (motif) motif.value = '';
        });
        $ready(document).on('hidden.bs.modal', '#permissionModal, #editAccountModal', function () {
            var body = this.querySelector('.modal-body');
            if (body) body.innerHTML = spinnerHtml();
        });
    }

    document.addEventListener('pb:livepage', syncAllGerantSections);
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncAllGerantSections);
    } else {
        syncAllGerantSections();
    }
})();
