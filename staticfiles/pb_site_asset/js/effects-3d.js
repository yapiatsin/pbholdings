/* ============================================================
   EFFETS 3D INTERACTIFS — P&BEntreprise
   Tilt souris, parallaxe héros, révélation au scroll
   ============================================================ */

(function() {
    'use strict';

    /* ----------------------------------------------------------------
       TILT 3D AU MOUVEMENT DE SOURIS
       Donne un effet de profondeur réaliste sur les cartes
    ---------------------------------------------------------------- */
    function initCardTilt(selector, options) {
        var defaults = {
            maxTilt: 12,
            perspective: 1000,
            speedIn: 100,
            speedOut: 500,
            scale: 1.03,
            glare: true
        };
        var opts = Object.assign({}, defaults, options || {});

        document.querySelectorAll(selector).forEach(function(el) {
            /* Couche de reflet (glare) */
            var glareEl = null;
            // if (opts.glare) {
            //     glareEl = document.createElement('div');
            //     glareEl.style.cssText = [
            //         'position:absolute',
            //         'inset:0',
            //         'border-radius:inherit',
            //         'pointer-events:none',
            //         'z-index:3',
            //         'opacity:0',
            //         'transition:opacity 0.4s ease',
            //         'background:linear-gradient(135deg,rgba(255,255,255,0.18) 0%,rgba(255,255,255,0) 60%)'
            //     ].join(';');
            //     el.style.position = el.style.position || 'relative';
            //     el.appendChild(glareEl);
            // }

            // el.addEventListener('mouseenter', function() {
            //     el.style.transition =
            //         'transform ' + opts.speedIn + 'ms cubic-bezier(0.23,1,0.32,1)';
            // });

            el.addEventListener('mousemove', function(e) {
                var rect = el.getBoundingClientRect();
                var x = e.clientX - rect.left;
                var y = e.clientY - rect.top;
                var cx = rect.width / 2;
                var cy = rect.height / 2;

                var rotX = ((y - cy) / cy) * -opts.maxTilt;
                var rotY = ((x - cx) / cx) * opts.maxTilt;

                el.style.transform =
                    'perspective(' + opts.perspective + 'px)' +
                    ' rotateX(' + rotX + 'deg)' +
                    ' rotateY(' + rotY + 'deg)' +
                    ' scale3d(' + opts.scale + ',' + opts.scale + ',' + opts.scale + ')';

                /* Déplace le reflet selon la position du curseur */
                if (glareEl) {
                    var glareX = (x / rect.width) * 100;
                    var glareY = (y / rect.height) * 100;
                    glareEl.style.opacity = '1';
                    glareEl.style.background =
                        'radial-gradient(circle at ' + glareX + '% ' + glareY + '%,' +
                        'rgba(255,255,255,0.22) 0%,rgba(255,255,255,0) 65%)';
                }
            });

            el.addEventListener('mouseleave', function() {
                el.style.transition =
                    'transform ' + opts.speedOut + 'ms cubic-bezier(0.25,1,0.35,1)';
                el.style.transform =
                    'perspective(' + opts.perspective + 'px)' +
                    ' rotateX(0deg) rotateY(0deg) scale3d(1,1,1)';
                if (glareEl) {
                    glareEl.style.opacity = '0';
                }
            });
        });
    }


    /* ================================================================
       PAGE HEADER — ZOOM D'ENTRÉE + PARALLAXE 3D SOURIS
       Curseur gauche→droite : background droite→gauche (et vice-versa)
    ================================================================ */
    /* ================================================================
       BLOG SECTION — SLIDE-IN AU SCROLL (gauche ← / → droite)
       Tout en inline style pour éviter tout conflit de spécificité.
       Se ré-déclenche à chaque passage dans le viewport.
    ================================================================ */
    function initBlogSlideIn() {
        var sections = Array.from(
            document.querySelectorAll('.blog-section-3--index3-stack')
        );
        if (!sections.length) return;

        /* GSAP et ScrollTrigger sont chargés par main.js — on les réutilise */
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

        var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduced) return;

        sections.forEach(function(section) {
            var cols = Array.from(section.querySelectorAll('.col-md-6'));
            if (cols.length < 2) return;

            var L = cols[0]; /* colonne gauche */
            var R = cols[1]; /* colonne droite  */

            /* État initial : hors-champ */
            gsap.set(L, {
                opacity: 0,
                x: -110,
                willChange: 'transform, opacity'
            });
            gsap.set(R, {
                opacity: 0,
                x: 110,
                willChange: 'transform, opacity'
            });

            /* Animation entrée */
            function slideIn() {
                gsap.to(L, {
                    opacity: 1,
                    x: 0,
                    duration: 0.82,
                    ease: 'power3.out',
                    overwrite: 'auto'
                });
                gsap.to(R, {
                    opacity: 1,
                    x: 0,
                    duration: 0.82,
                    ease: 'power3.out',
                    delay: 0.13,
                    overwrite: 'auto'
                });
            }

            /* Animation sortie (reset instantané pour rejouer à chaque scroll) */
            function slideOut() {
                gsap.set(L, {
                    opacity: 0,
                    x: -110
                });
                gsap.set(R, {
                    opacity: 0,
                    x: 110
                });
            }

            ScrollTrigger.create({
                trigger: section,
                start: 'top 88%',
                /* déclenche quand le haut de la section atteint 88% du viewport */
                end: 'bottom 0%',
                onEnter: slideIn,
                onLeave: slideOut,
                onEnterBack: slideIn,
                onLeaveBack: slideOut,
            });
        });
    }


    function initPageHeaderParallax() {
        var section = document.querySelector('.page-header');
        if (!section) return;
        var bg = section.querySelector('.bg-img');
        var shapes = Array.from(section.querySelectorAll('.shape'));
        if (!bg) return;

        /* --- Lerp vars --- */
        var targetX = 0,
            targetY = 0;
        var currentX = 0,
            currentY = 0;
        var rafId = null;
        var isHovering = false;
        var parallaxLive = false; /* true une fois le zoom terminé */
        var SCALE = 1.14;
        var MAX_X = 32;
        var MAX_Y = 14;
        var LERP = 0.055;

        function lerp(a, b, t) {
            return a + (b - a) * t;
        }

        function tick() {
            currentX = lerp(currentX, targetX, LERP);
            currentY = lerp(currentY, targetY, LERP);
            var rx = Math.round(currentX * 1000) / 1000;
            var ry = Math.round(currentY * 1000) / 1000;

            bg.style.transform =
                'scale(' + SCALE + ') translateX(' + rx + 'px) translateY(' + ry + 'px)';

            shapes.forEach(function(s, i) {
                var f = 0.18 + i * 0.08;
                s.style.transform =
                    'translateX(' + (rx * f) + 'px) translateY(' + (ry * f * 0.6) + 'px)';
            });

            if (isHovering ||
                Math.abs(currentX - targetX) > 0.05 ||
                Math.abs(currentY - targetY) > 0.05) {
                rafId = requestAnimationFrame(tick);
            } else {
                rafId = null;
            }
        }

        /* ---- ZOOM D'ENTRÉE : attend que l'image soit chargée ---- */
        function startZoom() {
            /* Force un reflow avant d'ajouter la classe de transition */
            void bg.offsetWidth;
            bg.classList.add('ph-zoom-ready');

            /* Passe en mode parallaxe après la fin de la transition CSS (1.7s).
               On gèle l'état en inline-style AVANT le changement de classe
               pour éviter tout flash (retour à scale(1.35)/opacity:0). */
            setTimeout(function() {
                bg.style.transform = 'scale(' + SCALE + ') translateX(0px) translateY(0px)';
                bg.style.opacity = '1';
                bg.classList.remove('ph-zoom-ready');
                bg.classList.add('ph-parallax-active');
                parallaxLive = true;
            }, 1750);
        }

        /* Récupère l'URL depuis l'attribut data-background OU le style inline */
        function resolveImgUrl() {
            var inline = bg.style.backgroundImage;
            if (inline) {
                var m = inline.match(/url\(["']?([^"')]+)["']?\)/i);
                return m ? m[1] : null;
            }
            return bg.getAttribute('data-background') || null;
        }

        function tryStartZoom() {
            var url = resolveImgUrl();
            if (!url) {
                /* main.js n'a pas encore appliqué le data-background → attendre */
                setTimeout(tryStartZoom, 80);
                return;
            }
            var img = new Image();
            img.onload = startZoom;
            img.onerror = startZoom; /* même en cas d'erreur, on anime */
            img.src = url;
        }

        /* Lance la détection (main.js tourne juste avant effects-3d.js) */
        tryStartZoom();

        /* ---- PARALLAXE SOURIS ---- */
        section.addEventListener('mousemove', function(e) {
            if (!parallaxLive) return;
            var rect = section.getBoundingClientRect();
            var cx = rect.width / 2;
            var cy = rect.height / 2;
            var dx = (e.clientX - rect.left - cx) / cx;
            var dy = (e.clientY - rect.top - cy) / cy;

            targetX = -dx * MAX_X; /* opposé au curseur */
            targetY = -dy * MAX_Y;

            isHovering = true;
            if (!rafId) rafId = requestAnimationFrame(tick);
        });

        section.addEventListener('mouseleave', function() {
            isHovering = false;
            targetX = 0;
            targetY = 0;
            if (!rafId) rafId = requestAnimationFrame(tick);
        });
    }


    /* ----------------------------------------------------------------
       INITIALISATION
    ---------------------------------------------------------------- */
    function init() {
        /* Tilt souris sur les cartes */
        initCardTilt('.promo-item', {
            maxTilt: 8,
            perspective: 1100,
            scale: 1.02
        });
        initCardTilt('.process-item', {
            maxTilt: 8,
            perspective: 950,
            scale: 1.02
        });
        initCardTilt('.team-counter', {
            maxTilt: 12,
            perspective: 600,
            scale: 1.04,
            glare: false
        });

        /* Effets globaux (guards typeof pour éviter ReferenceError) */
        if (typeof initHeroParallax === 'function') initHeroParallax();
        if (typeof initAboutTilt === 'function') initAboutTilt();
        if (typeof initCtaTilt === 'function') initCtaTilt();
        if (typeof initParticleDepth === 'function') initParticleDepth();
        if (typeof init3DScrollReveal === 'function') init3DScrollReveal();

        /* Cube 3D personnalisé (témoignages) */
        if (typeof initCustomCube3D === 'function') initCustomCube3D();

        /* Parallaxe 3D souris sur le page-header */
        initPageHeaderParallax();

        /* Slide-in gauche/droite au scroll sur la section blog */
        initBlogSlideIn();

        /* Plaques glassmorphism flottantes + léger parallax scroll */
        initGlassDecor();
    }

    /**
     * PRNG déterministe par section : dispositions différentes entre sections,
     * variation à chaque chargement (salt).
     */
    function pbGlassMulberry32(seed) {
        return function() {
            var t = (seed += 0x6d2b79f5);
            t = Math.imul(t ^ (t >>> 15), t | 1);
            t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    /**
     * Place au plus 3 shards : trois gammes de taille distinctes (petit / moyen / grand),
     * répartis sur les bords (haut, milieu, bas) pour éviter le bloc contenu central.
     */
    function layoutGlassShardsPlacements(decor, sectionIndex) {
        var shards = decor.querySelectorAll('.pb-glass-decor__shard');
        if (shards.length < 3) {
            return;
        }

        /* About index-3 : disposition fixe calquée sur la maquette */
        var aboutSection = decor.closest('.about-section-3');
        if (aboutSection) {
            var narrowAbt = window.innerWidth < 576;
            var mediumAbt = window.innerWidth < 992;

            function setAbtShard(shard, cfg) {
                shard.style.left = '';
                shard.style.right = '';
                shard.style.top = '';
                shard.style.bottom = '';
                shard.style.width = cfg.w + 'px';
                shard.style.height = cfg.h + 'px';
                shard.style.top = cfg.top;
                if (cfg.left != null) shard.style.left = cfg.left;
                if (cfg.right != null) shard.style.right = cfg.right;
            }

            if (narrowAbt) {
                setAbtShard(shards[0], {
                    w: 52,
                    h: 56,
                    top: '2%',
                    left: '5%'
                });
                setAbtShard(shards[1], {
                    w: 64,
                    h: 70,
                    top: '12%',
                    right: '4%'
                });
                setAbtShard(shards[2], {
                    w: 58,
                    h: 64,
                    top: '72%',
                    left: '30%'
                });
            } else if (mediumAbt) {
                setAbtShard(shards[0], {
                    w: 68,
                    h: 74,
                    top: '1%',
                    left: '8%'
                });
                setAbtShard(shards[1], {
                    w: 88,
                    h: 96,
                    top: '10%',
                    right: '3%'
                });
                setAbtShard(shards[2], {
                    w: 76,
                    h: 84,
                    top: '70%',
                    left: '34%'
                });
            } else {
                setAbtShard(shards[0], {
                    w: 115,
                    h: 108,
                    top: '0%',
                    left: '32%'
                });
                setAbtShard(shards[1], {
                    w: 104,
                    h: 112,
                    top: '8%',
                    right: '18%'
                });
                setAbtShard(shards[2], {
                    w: 120,
                    h: 120,
                    top: '58%',
                    left: '45%'
                });
            }
            return;
        }

        /* CTA-2 (section offres) : disposition calquée sur la maquette */
        var cta2Section = decor.closest('.pb-glass-section--cta2');
        if (cta2Section) {
            var narrowC2 = window.innerWidth < 576;
            var mediumC2 = window.innerWidth < 992;

            function setC2Shard(shard, cfg) {
                shard.style.left = '';
                shard.style.right = '';
                shard.style.top = '';
                shard.style.bottom = '';
                shard.style.width = cfg.w + 'px';
                shard.style.height = cfg.h + 'px';
                shard.style.top = cfg.top;
                if (cfg.left != null) shard.style.left = cfg.left;
                if (cfg.right != null) shard.style.right = cfg.right;
            }

            if (narrowC2) {
                setC2Shard(shards[0], {
                    w: 52,
                    h: 56,
                    top: '4%',
                    left: '3%'
                });
                setC2Shard(shards[1], {
                    w: 46,
                    h: 50,
                    top: '18%',
                    right: '6%'
                });
                setC2Shard(shards[2], {
                    w: 56,
                    h: 60,
                    top: '68%',
                    right: '28%'
                });
            } else if (mediumC2) {
                setC2Shard(shards[0], {
                    w: 68,
                    h: 74,
                    top: '2%',
                    left: '4%'
                });
                setC2Shard(shards[1], {
                    w: 58,
                    h: 64,
                    top: '16%',
                    right: '8%'
                });
                setC2Shard(shards[2], {
                    w: 66,
                    h: 72,
                    top: '66%',
                    right: '32%'
                });
            } else {
                setC2Shard(shards[0], {
                    w: 100,
                    h: 100,
                    top: '8%',
                    left: '12%'
                });
                setC2Shard(shards[1], {
                    w: 110,
                    h: 110,
                    top: '2%',
                    right: '15%'
                });
                setC2Shard(shards[2], {
                    w: 170,
                    h: 170,
                    top: '62%',
                    right: '35%'
                });
            }
            return;
        }

        /* CTA index-3 : disposition fixe proche de la maquette fournie */
        var ctaSection = decor.closest('.cta-section-3--index3-stack');
        if (ctaSection) {
            var narrowCTA = window.innerWidth < 576;
            var mediumCTA = window.innerWidth < 992;

            function setCtaShard(shard, cfg) {
                shard.style.left = '';
                shard.style.right = '';
                shard.style.top = '';
                shard.style.bottom = '';
                shard.style.width = cfg.w + 'px';
                shard.style.height = cfg.h + 'px';
                shard.style.top = cfg.top;
                if (cfg.left != null) shard.style.left = cfg.left;
                if (cfg.right != null) shard.style.right = cfg.right;
            }

            if (narrowCTA) {
                setCtaShard(shards[0], {
                    w: 54,
                    h: 54,
                    top: '30%',
                    left: '6%'
                });
                setCtaShard(shards[1], {
                    w: 34,
                    h: 34,
                    top: '6%',
                    left: '52%'
                });
                setCtaShard(shards[2], {
                    w: 64,
                    h: 64,
                    top: '64%',
                    right: '16%'
                });
            } else if (mediumCTA) {
                setCtaShard(shards[0], {
                    w: 74,
                    h: 74,
                    top: '22%',
                    left: '6%'
                });
                setCtaShard(shards[1], {
                    w: 42,
                    h: 42,
                    top: '20%',
                    left: '54%'
                });
                setCtaShard(shards[2], {
                    w: 94,
                    h: 94,
                    top: '56%',
                    right: '60%'
                });
            } else {
                setCtaShard(shards[0], {
                    w: 94,
                    h: 94,
                    top: '18%',
                    left: '8%'
                });
                setCtaShard(shards[1], {
                    w: 48,
                    h: 48,
                    top: '1%',
                    left: '58%'
                });
                setCtaShard(shards[2], {
                    w: 128,
                    h: 128,
                    top: '52%',
                    right: '8%'
                });
            }
            return;
        }

        var salt = (Date.now() & 0xfffffff) ^ (sectionIndex * 0x9e3779b9);
        var rnd = pbGlassMulberry32(salt);
        var narrow = window.innerWidth < 576;
        var medium = window.innerWidth < 992;

        /* [petit, moyen, grand] en px — écarts nets entre les trois */
        var tiers = narrow ? [
                [32, 44],
                [50, 64],
                [68, 86]
            ] :
            medium ? [
                [40, 54],
                [62, 82],
                [90, 112]
            ] : [
                [46, 62],
                [74, 96],
                [102, 132]
            ];

        /* Quelle taille (0/1/2) pour le shard i — toujours les trois paliers, ordre mélangé */
        var tierOrder = [0, 1, 2];
        for (var s = 2; s > 0; s--) {
            var ji = Math.floor(rnd() * (s + 1));
            var swap = tierOrder[s];
            tierOrder[s] = tierOrder[ji];
            tierOrder[ji] = swap;
        }

        function widthForSlot(slot) {
            var ti = tierOrder[slot];
            var b = tiers[ti];
            return b[0] + rnd() * (b[1] - b[0]);
        }

        function clearEdges(el) {
            el.style.left = '';
            el.style.right = '';
            el.style.top = '';
            el.style.bottom = '';
        }

        function setShard(shard, slot, topPct, leftPct, rightPct) {
            clearEdges(shard);
            var w = widthForSlot(slot);
            var aspect = 0.88 + rnd() * 0.24;
            var h = Math.round(w * aspect);
            shard.style.width = Math.round(w) + 'px';
            shard.style.height = h + 'px';
            shard.style.top = topPct.toFixed(2) + '%';
            if (leftPct != null) {
                shard.style.left = leftPct.toFixed(2) + '%';
            }
            if (rightPct != null) {
                shard.style.right = rightPct.toFixed(2) + '%';
            }
        }

        /* Miroir gauche/droite selon section + tirage : triangle sur les marges */
        var mirror = (sectionIndex + Math.floor(rnd() * 2)) % 2 === 1;

        if (!mirror) {
            setShard(
                shards[0],
                0,
                7 + rnd() * 16,
                1 + rnd() * 12,
                null
            );
            setShard(
                shards[1],
                1,
                38 + rnd() * 20,
                null,
                2 + rnd() * 14
            );
            var bottomL = rnd() > 0.5;
            setShard(
                shards[2],
                2,
                66 + rnd() * 18,
                bottomL ? 2 + rnd() * 11 : null,
                bottomL ? null : 1 + rnd() * 12
            );
        } else {
            setShard(
                shards[0],
                0,
                7 + rnd() * 16,
                null,
                1 + rnd() * 12
            );
            setShard(
                shards[1],
                1,
                38 + rnd() * 20,
                2 + rnd() * 14,
                null
            );
            var bottomL2 = rnd() > 0.5;
            setShard(
                shards[2],
                2,
                66 + rnd() * 18,
                bottomL2 ? 2 + rnd() * 11 : null,
                bottomL2 ? null : 1 + rnd() * 12
            );
        }
    }

    /**
     * Décor « glace » : placement aléatoire par section + flottement GSAP + scroll (ScrollTrigger).
     */
    function initGlassDecor() {
        var sections = document.querySelectorAll('.pb-glass-section');
        if (!sections.length) {
            return;
        }

        sections.forEach(function(section, si) {
            var decor = section.querySelector('.pb-glass-decor');
            if (decor) {
                layoutGlassShardsPlacements(decor, si);
            }
        });

        var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduceMotion) {
            return;
        }
        if (typeof gsap === 'undefined') {
            return;
        }

        if (typeof ScrollTrigger !== 'undefined' && gsap.registerPlugin) {
            try {
                gsap.registerPlugin(ScrollTrigger);
            } catch (e) {
                /* déjà enregistré */
            }
        }

        var floatEase = 'sine.inOut';
        var shardMotion = [{
                baseDeg: -6,
                x: 12,
                y: 18,
                dRot: 5
            },
            {
                baseDeg: 5,
                x: -11,
                y: 14,
                dRot: -4
            },
            {
                baseDeg: -4,
                x: 9,
                y: 20,
                dRot: 4
            }
        ];

        sections.forEach(function(section) {
            var decor = section.querySelector('.pb-glass-decor');
            if (!decor) {
                return;
            }

            if (typeof ScrollTrigger !== 'undefined') {
                gsap.fromTo(
                    decor, {
                        y: 0
                    }, {
                        y: 48,
                        ease: 'none',
                        scrollTrigger: {
                            trigger: section,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: 0.75
                        }
                    }
                );
            }

            decor.querySelectorAll('.pb-glass-decor__shard').forEach(function(shard, i) {
                var m = shardMotion[i % shardMotion.length];
                var dur = 4.4 + (i % 3) * 0.9;
                gsap.fromTo(
                    shard, {
                        x: 0,
                        y: 0,
                        rotation: m.baseDeg
                    }, {
                        x: m.x,
                        y: m.y,
                        rotation: m.baseDeg + m.dRot,
                        duration: dur,
                        ease: floatEase,
                        repeat: -1,
                        yoyo: true,
                        delay: i * 0.18
                    }
                );
            });
        });

        if (typeof ScrollTrigger !== 'undefined') {
            ScrollTrigger.refresh();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

/* ============================================================
   CURSEUR PREMIUM — P&BEntreprise
   Actif uniquement sur desktop (≥ 992px)
   ============================================================ */
(function() {
    'use strict';

    /* --- Seulement sur desktop --- */
    if (window.innerWidth < 992) return;

    /* ----------------------------------------------------------------
       CRÉATION DES ÉLÉMENTS
    ---------------------------------------------------------------- */
    var wrapper = document.createElement('div');
    wrapper.className = 'pb-cursor';

    var dot = document.createElement('div');
    dot.className = 'pb-cursor__dot';

    var ring = document.createElement('div');
    ring.className = 'pb-cursor__ring';

    var label = document.createElement('span');
    label.className = 'pb-cursor__label';
    ring.appendChild(label);

    wrapper.appendChild(dot);
    wrapper.appendChild(ring);
    document.body.appendChild(wrapper);

    /* ----------------------------------------------------------------
       TRACKING DE POSITION
    ---------------------------------------------------------------- */
    var mouseX = -200,
        mouseY = -200; /* démarrage hors écran */
    var ringX = -200,
        ringY = -200;
    var lerp = 0.13; /* vitesse d'élasticité de l'anneau */
    var rafId;

    /* Anneau suit avec interpolation linéaire (lerp) */
    function animateRing() {
        ringX += (mouseX - ringX) * lerp;
        ringY += (mouseY - ringY) * lerp;
        ring.style.left = ringX.toFixed(2) + 'px';
        ring.style.top = ringY.toFixed(2) + 'px';
        rafId = requestAnimationFrame(animateRing);
    }
    rafId = requestAnimationFrame(animateRing);

    /* Dot suit exactement */
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        dot.style.left = mouseX + 'px';
        dot.style.top = mouseY + 'px';

        /* Rend visible dès le premier mouvement */
        if (wrapper.style.visibility !== 'visible') {
            wrapper.style.visibility = 'visible';
        }
    });

    /* ----------------------------------------------------------------
       GESTIONNAIRE D'ÉTATS
    ---------------------------------------------------------------- */
    var currentState = '';
    var stateStack = []; /* pile pour gérer les surcharges */

    function pushState(state, labelText) {
        stateStack.push({
            state: state,
            label: labelText || ''
        });
        applyTopState();
    }

    function popState(state) {
        stateStack = stateStack.filter(function(s) {
            return s.state !== state;
        });
        applyTopState();
    }

    function applyTopState() {
        var top = stateStack[stateStack.length - 1];
        var newState = top ? top.state : '';
        var newLabel = top ? top.label : '';

        if (newState === currentState) return;
        currentState = newState;

        /* Classes d'état */
        wrapper.className = 'pb-cursor' +
            (newState ? ' pb-cursor--' + newState : '') +
            (newLabel ? '' : '');

        /* Label */
        label.textContent = newLabel;
    }

    /* ----------------------------------------------------------------
       ÉVÉNEMENTS HOVER — contexte-aware
    ---------------------------------------------------------------- */

    /* Liens simples */
    document.querySelectorAll('a:not(.bz-primary-btn)').forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            pushState('link');
        });
        el.addEventListener('mouseleave', function() {
            popState('link');
        });
    });

    /* Boutons CTA */
    document.querySelectorAll('.bz-primary-btn, button').forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            pushState('button');
        });
        el.addEventListener('mouseleave', function() {
            popState('button');
        });
    });

    /* Cartes interactives → label "Voir →" */
    document.querySelectorAll(
        '.promo-item, .process-item, .team-card'
    ).forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            pushState('card', 'Voir →');
        });
        el.addEventListener('mouseleave', function() {
            popState('card');
        });
    });

    /* Images / sections photo → label "Zoom" */
    document.querySelectorAll(
        '.about-img-3d-scroll, .strength-mask-img'
    ).forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            pushState('zoom', 'Zoom');
        });
        el.addEventListener('mouseleave', function() {
            popState('zoom');
        });
    });

    /* Swipers → label "Drag" */
    document.querySelectorAll('.swiper').forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            pushState('drag', 'P&B');
        });
        el.addEventListener('mouseleave', function() {
            popState('drag');
        });
    });

    /* ----------------------------------------------------------------
       ANIMATION AU CLIC
    ---------------------------------------------------------------- */
    document.addEventListener('mousedown', function() {
        wrapper.classList.add('pb-cursor--click');
    });
    document.addEventListener('mouseup', function() {
        wrapper.classList.remove('pb-cursor--click');
    });

    /* ----------------------------------------------------------------
       MASQUAGE QUAND LE CURSEUR SORT DE LA FENÊTRE
    ---------------------------------------------------------------- */
    document.addEventListener('mouseleave', function() {
        wrapper.classList.add('pb-cursor--hidden');
    });
    document.addEventListener('mouseenter', function() {
        wrapper.classList.remove('pb-cursor--hidden');
    });

    /* ----------------------------------------------------------------
       REDIMENSIONNEMENT : désactive sur mobile
    ---------------------------------------------------------------- */
    window.addEventListener('resize', function() {
        if (window.innerWidth < 992) {
            cancelAnimationFrame(rafId);
            wrapper.style.display = 'none';
        } else {
            wrapper.style.display = '';
            rafId = requestAnimationFrame(animateRing);
        }
    });

})();