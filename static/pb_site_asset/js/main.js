/* ============ Main JS ============ */

(function($) {
    "use strict";

    //Toggle Js
    $('.rr-checkout-login-form-reveal-btn').on('click', function() {
        $('#rrReturnCustomerLoginForm').slideToggle(400);
    });

    $('.rr-checkout-coupon-form-reveal-btn').on('click', function() {
        $('#rrCheckoutCouponForm').slideToggle(400);
    });


    /*======================================
        Preloader activation
    ========================================*/
    $(window).on("load", function(event) {
        $("#preloader").delay(1000).fadeOut(500);
        // Text Animation
        setTimeout(() => {
            var hasAnim = $(".anim-text");
            hasAnim.each(function() {
                var $this = $(this);
                var splitto = new SplitType($this, {
                    types: "lines, chars",
                    className: "char",
                });
                var chars = $this.find(".char");
                gsap.fromTo(
                    chars, {
                        y: "100%"
                    }, {
                        y: "0%",
                        duration: 0.9,
                        stagger: 0.03,
                        ease: "power2.out",
                    }
                );
            });
        }, 1000);
    });

    $(".preloader-close").on("click", function() {
        $("#preloader").delay(0).fadeOut(500);
    });

    $(document).ready(function() {

        /* Top bar adresse : double du texte pour marque CSS continue (.top-bar-location-marquee) */
        document.querySelectorAll(".top-bar-location-marquee__track").forEach(function(track) {
            var texts = track.querySelectorAll(".top-bar-location-marquee__text");
            if (texts.length !== 1) {
                return;
            }
            var duplicate = texts[0].cloneNode(true);
            duplicate.setAttribute("aria-hidden", "true");
            track.appendChild(duplicate);
        });

        if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
            $('body').addClass('firefox');
        }

        var header = $(".header"),
            stickyHeader = $(".primary-header");

        function menuSticky(w) {
            if (w.matches) {

                $(window).on("scroll", function() {
                    var scroll = $(window).scrollTop();
                    if (scroll >= 110) {
                        stickyHeader.addClass("fixed");
                    } else {
                        stickyHeader.removeClass("fixed");
                    }
                });
                if ($(".header").length > 0) {
                    var headerHeight = document.querySelector(".header"),
                        setHeaderHeight = headerHeight.offsetHeight;
                    header.each(function() {
                        $(this).css({
                            'height': setHeaderHeight + 'px'
                        });
                    });
                }
            }
        }

        var minWidth = window.matchMedia("(min-width: 0px)");
        if (header.hasClass("sticky-active")) {
            menuSticky(minWidth);
        }

        // Barre fixe bas d'écran : apparaît après 300px de scroll
        (function() {
            var bar = document.getElementById('pb-bottom-bar');
            if (!bar) return;
            var shown = false;
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300 && !shown) {
                    bar.classList.add('is-visible');
                    shown = true;
                } else if (window.pageYOffset <= 300 && shown) {
                    bar.classList.remove('is-visible');
                    shown = false;
                }
            }, {
                passive: true
            });
        })();

        // Index-3: panneau glass du hero
        // - masqué dès qu'on remonte hors du hero
        // - réaffiché quand la section hero revient à l'écran
        (function() {
            var panel = document.querySelector('.pb-hero-glass-panel');
            var heroSection = document.querySelector('.hero-section-3.hero-slider-3');
            if (!panel || !heroSection) return;

            var lastScrollY = window.pageYOffset || 0;
            var heroVisible = false;
            var isShown = false;
            var hideTimer = null;
            var scrollDebounceTimer = null;

            function animatePanel(show) {
                if (show === isShown) return;
                isShown = show;

                if (hideTimer) {
                    clearTimeout(hideTimer);
                    hideTimer = null;
                }

                if (show) {
                    panel.style.visibility = 'visible';
                    panel.classList.remove('is-visible');
                    window.requestAnimationFrame(function() {
                        panel.classList.add('is-visible');
                    });
                } else {
                    panel.classList.remove('is-visible');
                    hideTimer = window.setTimeout(function() {
                        if (!isShown) {
                            panel.style.visibility = 'hidden';
                        }
                    }, 320);
                }
            }

            function syncPanelVisibility() {
                animatePanel(heroVisible);
            }

            panel.classList.remove('is-visible');
            panel.style.visibility = 'hidden';

            if ('IntersectionObserver' in window) {
                var observer = new IntersectionObserver(function(entries) {
                    heroVisible = entries[0] && entries[0].isIntersecting;
                    syncPanelVisibility();
                }, {
                    threshold: 0.2
                });
                observer.observe(heroSection);
            } else {
                function fallbackCheck() {
                    var rect = heroSection.getBoundingClientRect();
                    heroVisible = rect.bottom > 0 && rect.top < window.innerHeight * 0.85;
                    syncPanelVisibility();
                }

                fallbackCheck();
                window.addEventListener('scroll', fallbackCheck, {
                    passive: true
                });
                window.addEventListener('resize', fallbackCheck, {
                    passive: true
                });
            }

            window.addEventListener('scroll', function() {
                var currentY = window.pageYOffset || 0;
                var scrollingUp = currentY < lastScrollY;

                if (scrollingUp) {
                    // Masquer dès qu'on remonte
                    animatePanel(false);
                } else if (heroVisible) {
                    // Remontre si on descend et que le hero est visible
                    animatePanel(true);
                }

                // Resync après arrêt du scroll (debounce 420ms)
                if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer);
                scrollDebounceTimer = setTimeout(function() {
                    syncPanelVisibility();
                }, 420);

                lastScrollY = currentY;
            }, {
                passive: true
            });
        })();

        // Index-3: bouton "Decouvrir" -> scroll promo avec section à 10% du viewport
        $(".js-scroll-to-promo").on("click", function(e) {
            e.preventDefault();
            var target = document.querySelector("#promo-section");
            if (!target) return;
            var targetTop = target.getBoundingClientRect().top + window.pageYOffset;
            var offset10vh = window.innerHeight * 0.10;
            var destination = Math.max(0, targetTop - offset10vh);
            window.scrollTo({
                top: destination,
                behavior: "smooth"
            });
        });

        //Mobile Menu Js
        $(".mobile-menu-items").meanmenu({
            meanMenuContainer: ".side-menu-wrap",
            meanScreenWidth: "992",
            meanMenuCloseSize: "30px",
            meanRemoveAttrs: true,
            meanExpand: ['<i class="fa-solid fa-caret-down"></i>'],
        });

        // Mobile Sidemenu
        $(".mobile-side-menu-toggle").on("click", function() {
            $(".mobile-side-menu, .mobile-side-menu-overlay").toggleClass("is-open");
        });

        $(".mobile-side-menu-close, .mobile-side-menu-overlay").on("click", function() {
            $(".mobile-side-menu, .mobile-side-menu-overlay").removeClass("is-open");
        });

        // Popup Search Box
        $(function() {
            $("#popup-search-box").removeClass("toggled");

            $(".dl-search-icon").on("click", function(e) {
                e.stopPropagation();
                $("#popup-search-box").toggleClass("toggled");
                $("#popup-search").focus();
            });

            $("#popup-search-box input").on("click", function(e) {
                e.stopPropagation();
            });

            $("#popup-search-box, body").on("click", function() {
                $("#popup-search-box").removeClass("toggled");
            });
        });

        // Popup Sidebox
        function sideBox() {
            $("body").removeClass("open-sidebar");
            $(document).on("click", ".sidebar-trigger", function(e) {
                e.preventDefault();
                $("body").toggleClass("open-sidebar");
            });
            $(document).on("click", ".sidebar-trigger.close, #sidebar-overlay", function(e) {
                e.preventDefault();
                $("body.open-sidebar").removeClass("open-sidebar");
            });
        }

        sideBox();

        // Venobox Active
        $('.venobox').venobox({
            bgcolor: 'transparent',
            spinner: 'spinner-pulse',
            numeration: true,
            infinigall: true
        });

        // Data Background
        $("[data-background").each(function() {
            $(this).css("background-image", "url( " + $(this).attr("data-background") + "  )");
        });

        // Custom Cursor
        $("body").append('<div class="mt-cursor"></div>');
        var cursor = $(".mt-cursor"),
            linksCursor = $("a, .swiper-nav, button, .cursor-effect"),
            crossCursor = $(".cross-cursor");
        var cursorHalf = 14;
        if (cursor.length) {
            cursorHalf = cursor.outerWidth() / 2;
        }
        var lastMouseX = null,
            lastMouseY = null,
            currentDotX = 0,
            currentDotY = 0,
            targetDotX = 0,
            targetDotY = 0,
            dotMaxOffset = 6.5,
            dotReturnFriction = 0.86,
            dotFollow = 0.16;

        function animateCursorDot() {
            targetDotX *= dotReturnFriction;
            targetDotY *= dotReturnFriction;

            currentDotX += (targetDotX - currentDotX) * dotFollow;
            currentDotY += (targetDotY - currentDotY) * dotFollow;

            cursor.css({
                "--cursor-dot-x": currentDotX.toFixed(2) + "px",
                "--cursor-dot-y": currentDotY.toFixed(2) + "px",
            });

            window.requestAnimationFrame(animateCursorDot);
        }
        window.requestAnimationFrame(animateCursorDot);

        $(window).on("mousemove", function(e) {
            if (lastMouseX === null || lastMouseY === null) {
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;
            }

            var deltaX = e.clientX - lastMouseX;
            var deltaY = e.clientY - lastMouseY;
            var distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            if (distance > 0.001) {
                var normalizedX = deltaX / distance;
                var normalizedY = deltaY / distance;
                var push = Math.min(dotMaxOffset, 1.4 + distance * 0.35);
                targetDotX = normalizedX * push;
                targetDotY = normalizedY * push;
            }

            lastMouseX = e.clientX;
            lastMouseY = e.clientY;

            cursor.css({
                transform: "translate(" + (e.clientX - cursorHalf) + "px," + (e.clientY - cursorHalf) + "px)",
                visibility: "inherit",
            });
        });

        $(window).on("mouseleave", function() {
            targetDotX = 0;
            targetDotY = 0;
            lastMouseX = null;
            lastMouseY = null;
        });

        /* Odometer */
        $(".odometer").waypoint(
            function() {
                var odo = $(".odometer");
                odo.each(function() {
                    var countNumber = $(this).attr("data-count");
                    $(this).html(countNumber);
                });
            }, {
                offset: "80%",
                triggerOnce: true,
            }
        );

        // Wow JS Active
        new WOW().init();

        // Nice Select Js
        $("select").niceSelect();

        // Isotop
        $(".filter-items").imagesLoaded(function() {
            // Add isotope click function
            $(".project-filter li").on("click", function() {
                $(".project-filter li").removeClass("active");
                $(this).addClass("active");

                var selector = $(this).attr("data-filter");
                $(".filter-items").isotope({
                    filter: selector,
                    animationOptions: {
                        duration: 750,
                        easing: "linear",
                        queue: false,
                    },
                });
                return false;
            });

            $(".filter-items").isotope({
                itemSelector: ".single-item",
                layoutMode: "fitRows",
                fitRows: {
                    gutter: 0,
                },
            });
        });

        // Home Hero Slider (index-3)
        var heroSlider3 = document.querySelector(".hero-swiper-3");
        if (heroSlider3) {
            new Swiper(".hero-swiper-3", {
                slidesPerView: 1,
                loop: true,
                effect: "fade",
                fadeEffect: {
                    crossFade: true
                },
                speed: 1100,
                autoplay: {
                    delay: 5200,
                    disableOnInteraction: false,
                },
                pagination: {
                    el: ".hero-swiper-pagination-3",
                    clickable: true,
                },
            });
        }

        // Service Carousel
        var swiperProject = new Swiper(".project-carousel", {
            slidesPerView: 2,
            spaceBetween: 30,
            slidesPerGroup: 1,
            loop: true,
            autoplay: true,
            grabcursor: true,
            speed: 600,
            grabcursor: true,
            navigation: {
                nextEl: ".project-section .swiper-prev",
                prevEl: ".project-section .swiper-next",
            },
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                320: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                767: {
                    slidesPerView: 2,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 2,
                    slidesPerGroup: 1,
                },
            },
        });

        // Sponsor Carousel
        var swiperSponsor = new Swiper(".sponsor-carousel", {
            slidesPerView: 45,
            spaceBetween: 50,
            slidesPerGroup: 1,
            loop: true,
            autoplay: true,
            grabCursor: true,
            speed: 400,
            breakpoints: {
                320: {
                    slidesPerView: 2,
                    slidesPerGroup: 1,
                    spaceBetween: 25,
                },
                767: {
                    slidesPerView: 3,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 5,
                    slidesPerGroup: 1,
                },
            },
        });

        // Testi Carousel
        var swiperTesti = new Swiper(".testi-carousel", {
            slidesPerView: 2,
            spaceBetween: 30,
            slidesPerGroup: 1,
            loop: true,
            autoplay: true,
            grabcursor: true,
            speed: 600,
            grabcursor: true,
            navigation: {
                nextEl: ".testi-section .swiper-prev",
                prevEl: ".testi-section .swiper-next",
            },
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                320: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                767: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 2,
                    slidesPerGroup: 1,
                },
            },
        });

        // Testimonials cube (index-3) or classic carousel
        var testiCubeSwiperEl = document.querySelector(".testi-cube-swiper");
        if (testiCubeSwiperEl) {
            var swiperTestiCube = new Swiper(".testi-cube-swiper", {
                effect: "cube",
                grabCursor: true,
                loop: true,
                speed: 1200,
                cubeEffect: {
                    shadow: true,
                    slideShadows: true,
                    shadowOffset: 26,
                    shadowScale: 0.86,
                },
                autoplay: {
                    delay: 2600,
                    disableOnInteraction: false,
                    pauseOnMouseEnter: true,
                },
                pagination: {
                    el: ".testimonial-cube-section .testi-cube-pagination",
                    clickable: true,
                },
            });
        } else if (document.querySelector(".testi-carousel-2")) {
            var swiperTesti2 = new Swiper(".testi-carousel-2", {
                slidesPerView: 2,
                spaceBetween: 30,
                slidesPerGroup: 1,
                loop: true,
                autoplay: true,
                grabcursor: true,
                speed: 600,
                grabcursor: true,
                navigation: {
                    nextEl: ".testi-section .swiper-prev",
                    prevEl: ".testi-section .swiper-next",
                },
                pagination: {
                    el: ".swiper-pagination",
                    clickable: true,
                },
                breakpoints: {
                    320: {
                        slidesPerView: 1,
                        slidesPerGroup: 1,
                        spaceBetween: 30,
                    },
                    767: {
                        slidesPerView: 1,
                        slidesPerGroup: 1,
                        spaceBetween: 30,
                    },
                    1024: {
                        slidesPerView: 2,
                        slidesPerGroup: 1,
                    },
                },
            });
        }

        /* Particules arrière-plan — section témoignages cube (index-3) */
        var testiCubeParticles = document.getElementById("testi-cube-particles");
        if (testiCubeParticles && typeof tsParticles !== "undefined" && typeof tsParticles.load === "function") {
            var testiParticlesOpts = {
                fullScreen: {
                    enable: false,
                },
                background: {
                    color: {
                        value: "transparent",
                    },
                },
                fpsLimit: 60,
                particles: {
                    number: {
                        value: 28,
                        density: {
                            enable: true,
                            area: 900,
                        },
                    },
                    color: {
                        value: [
                            "#3998D0",
                            "#2EB6AF",
                            "#A9BD33",
                            "#FEC73B",
                            "#F89930",
                            "#F45623",
                            "#D62E32",
                            "#EC281C",
                        ],
                    },
                    shape: {
                        type: "circle",
                    },
                    opacity: {
                        value: 0.9,
                    },
                    size: {
                        value: {
                            min: 3,
                            max: 8,
                        },
                    },
                    move: {
                        enable: true,
                        speed: 1.4,
                        direction: "none",
                        random: true,
                        straight: false,
                        outModes: {
                            default: "bounce",
                        },
                    },
                },
                detectRetina: true,
            };
            var testiParticlesPromise = tsParticles.load({
                id: "testi-cube-particles",
                options: testiParticlesOpts,
            });
            if (testiParticlesPromise && typeof testiParticlesPromise.catch === "function") {
                testiParticlesPromise.catch(function() {
                    try {
                        tsParticles.load("testi-cube-particles", testiParticlesOpts);
                    } catch (err) {}
                });
            }
        }

        // Testi Carousel
        var swiperTesti = new Swiper(".testi-carousel-3", {
            slidesPerView: 3,
            spaceBetween: 30,
            slidesPerGroup: 1,
            loop: true,
            autoplay: true,
            grabcursor: true,
            speed: 600,
            grabcursor: true,
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                320: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                767: {
                    slidesPerView: 2,
                    slidesPerGroup: 1,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 3,
                    slidesPerGroup: 1,
                },
            },
        });

        // Testi Carousel
        var swiperPostthumb = new Swiper(".post-thumb-carousel", {
            slidesPerView: 1,
            spaceBetween: 10,
            slidesPerGroup: 1,
            loop: true,
            autoplay: true,
            grabcursor: true,
            speed: 600,
            grabcursor: true,
            navigation: {
                nextEl: ".post-thumb-carousel .swiper-prev",
                prevEl: ".post-thumb-carousel .swiper-next",
            },
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                320: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                    spaceBetween: 10,
                },
                767: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                    spaceBetween: 10,
                },
                1024: {
                    slidesPerView: 1,
                    slidesPerGroup: 1,
                },
            },
        });

        // Date Range Picker
        $(function() {
            $('input[name="daterange"]').daterangepicker({
                    opens: "center",
                },
                function(start, end, label) {
                    console.log(
                        "A new date selection was made: " + start.format("YYYY-MM-DD") + " to " + end.format("YYYY-MM-DD")
                    );
                }
            );
        });

        $(function() {
            $('input[name="birthday"]').daterangepicker({
                singleDatePicker: true,
                showDropdowns: true,
            });
        });


        //Swiper Slider For Shop
        var swiper = new Swiper(".product-gallary-thumb", {
            spaceBetween: 10,
            slidesPerView: 3,
            freeMode: true,
            watchSlidesProgress: true,
        });
        var swiper2 = new Swiper(".product-gallary", {
            spaceBetween: 10,
            loop: true,
            navigation: {
                nextEl: ".swiper-nav-next",
                prevEl: ".swiper-nav-prev",
            },
            thumbs: {
                swiper: swiper,
            },
        });

        // Stroke Text

        $(function() {
            let container_svg = $('.container-svg');
            let that, svg, text, bbox, width, height, calc_ratio, stroke_dasharray, new_value_stroke;
            let is_safari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
            let is_retina = false;
            if (matchMedia("(-webkit-min-device-pixel-ratio: 2), (min-device-pixel-ratio: 2), (min-resolution: 192dpi)").matches) {
                is_retina = true;
            }
            container_svg.each(function() {
                that = $(this);
                // Set viewBox size
                svg = $('svg', that);
                text = $('text', that);
                bbox = text[0].getBBox();
                width = that.width();
                height = bbox.height;
                svg.attr('viewBox', '0 0 ' + width + ' ' + height);
                // Set container height with ratio
                calc_ratio = (height * 100 / width);
                that.css('padding-bottom', calc_ratio + '%');
                if (is_safari) { // Safari fix
                    text.attr('y', '1em');
                }
                if (is_retina) {
                    stroke_dasharray = text.css('stroke-dasharray');
                    new_value_stroke = retina_stroke_dasharray(stroke_dasharray);
                    text.css('stroke-dasharray', new_value_stroke);
                }
            })
        })

        function retina_stroke_dasharray(value) {
            let array = value.split(",");
            for (let i = 0; i < array.length; i++) {
                array[i] = (parseInt(array[i]) * 2) + 'px';
            }
            return array.join(', ');
        }

        //Running Animated Text
        const scrollers = document.querySelectorAll(".scroller");

        if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            addAnimation();
        }

        function addAnimation() {
            scrollers.forEach((scroller) => {
                scroller.setAttribute("data-animated", true);

                const scrollerInner = scroller.querySelector(".scroller__inner");
                const scrollerContent = Array.from(scrollerInner.children);

                scrollerContent.forEach((item) => {
                    const duplicatedItem = item.cloneNode(true);
                    duplicatedItem.setAttribute("aria-hidden", true);
                    scrollerInner.appendChild(duplicatedItem);
                });
            });
        }

        // Image Reveal

        gsap.registerPlugin(ScrollTrigger);

        let revealContainers = document.querySelectorAll(".reveal");

        revealContainers.forEach((container) => {
            let image = container.querySelector("img");
            let tl = gsap.timeline({
                scrollTrigger: {
                    trigger: container,
                    toggleActions: "restart none none reset"
                }
            });

            tl.set(container, {
                autoAlpha: 1
            });
            tl.from(container, 1.5, {
                xPercent: -100,
                ease: Power2.out
            });
            tl.from(image, 1.5, {
                xPercent: 100,
                scale: 1.3,
                delay: -1.5,
                ease: Power2.out
            });
        });

        const images = document.querySelectorAll(".img-reveal");

        const removeOverlay = overlay => {
            let tl = gsap.timeline();

            tl.to(overlay, {
                duration: 1.4,
                ease: "Power2.easeInOut",
                width: "0%"
            });

            return tl;
        };

        const removeOverlayTopDown = overlay => {
            let tl = gsap.timeline();

            tl.to(overlay, {
                duration: 1.4,
                ease: "Power2.easeInOut",
                height: "0%"
            });

            return tl;
        };

        const scaleInImage = image => {
            let tl = gsap.timeline();

            tl.from(image, {
                duration: 1.4,
                scale: 1.4,
                ease: "Power2.easeInOut"
            });

            return tl;
        };

        images.forEach(image => {

            gsap.set(image, {
                visibility: "visible"
            });

            const overlay = image.querySelector('.img-overlay');
            const img = image.querySelector("img");

            if (image.classList.contains("about-img-3")) {
                gsap.set(overlay, {
                    width: "100%",
                    height: "100%",
                    transformOrigin: "top center"
                });

                const aboutTL = gsap.timeline({
                    paused: true
                });
                aboutTL
                    .to(overlay, {
                        height: "0%",
                        duration: 1.4,
                        ease: "power2.inOut"
                    })
                    .fromTo(img, {
                        scale: 1.35
                    }, {
                        scale: 1,
                        duration: 1.4,
                        ease: "power2.inOut"
                    }, "-=1.4");

                if (!("IntersectionObserver" in window)) {
                    image.classList.add("is-inview");
                    aboutTL.play();
                    return;
                }

                let aboutWasInView = false;
                const aboutIo = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add("is-inview");
                            if (!aboutWasInView) {
                                aboutTL.restart();
                            }
                            aboutWasInView = true;
                        } else {
                            entry.target.classList.remove("is-inview");
                            aboutTL.progress(0).pause();
                            aboutWasInView = false;
                        }
                    });
                }, {
                    threshold: 0.2
                });

                aboutIo.observe(image);
                return;
            }

            if (
                image.classList.contains("process-thumb") ||
                image.classList.contains("post-thumb")
            ) {
                // Dans .process-section-2--green-cards : animation one-shot (pas de reset au re-scroll)
                // L'image reste visible une fois révélée + le hover CSS peut zoomer librement
                var isGreenCards = !!image.closest('.process-section-2--green-cards');

                gsap.set(overlay, {
                    width: "100%",
                    height: "100%",
                    transformOrigin: "top center"
                });

                const topDownRevealTL = gsap.timeline({
                    paused: true,
                    onComplete: function() {
                        // Après l'animation, on nettoie le transform inline pour libérer le hover CSS
                        if (isGreenCards && img) {
                            gsap.set(img, { clearProps: "transform" });
                        }
                    }
                });
                topDownRevealTL
                    .add(removeOverlayTopDown(overlay))
                    .add(scaleInImage(img), "-=1.4");

                let topDownOptions = {
                    threshold: 0
                };

                if (isGreenCards) {
                    // One-shot : joue une seule fois, ne se remet jamais à zéro
                    var greenHasPlayed = false;
                    const greenIo = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting && !greenHasPlayed) {
                                topDownRevealTL.play();
                                greenHasPlayed = true;
                            }
                        });
                    }, topDownOptions);
                    greenIo.observe(image);
                } else {
                    // Comportement original pour les autres sections
                    const topDownIo = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                topDownRevealTL.play();
                            } else {
                                topDownRevealTL.progress(0).pause();
                            }
                        });
                    }, topDownOptions);
                    topDownIo.observe(image);
                }
                return;
            }

            const masterTL = gsap.timeline({
                paused: true
            });
            masterTL
                .add(removeOverlay(overlay))
                .add(scaleInImage(img), "-=1.4");


            let options = {
                threshold: 0
            }

            const io = new IntersectionObserver((entries, options) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        masterTL.play();
                    } else {
                        masterTL.progress(0).pause()
                    }
                });
            }, options);

            io.observe(image);
        });


        // Scroll Animation

        let typeSplit = new SplitType("[data-text-animation]", {
            types: "lines,words, chars",
            className: "line",
        });
        var text_animations = document.querySelectorAll(
            "[data-text-animation]"
        );

        function createScrollTrigger(triggerElement, timeline) {
            // Play tl when scrolled into view (60% from top of screen)
            ScrollTrigger.create({
                trigger: triggerElement,
                start: "top 80%",
                onEnter: () => timeline.play(),
                toggleClass: {
                    targets: triggerElement,
                    className: "active"
                }
            });
        }

        text_animations.forEach((animation) => {
            let type = "slide-up",
                duration = 0.75,
                offset = 80,
                stagger = 0.6,
                delay = 0,
                scroll = 1,
                split = "line",
                ease = "power2.out";
            // Set attribute
            if (animation.getAttribute("data-stagger")) {
                stagger = animation.getAttribute("data-stagger");
            }
            if (animation.getAttribute("data-duration")) {
                duration = animation.getAttribute("data-duration");
            }
            if (animation.getAttribute("data-text-animation")) {
                type = animation.getAttribute("data-text-animation");
            }
            if (animation.getAttribute("data-delay")) {
                delay = animation.getAttribute("data-delay");
            }
            if (animation.getAttribute("data-ease")) {
                ease = animation.getAttribute("data-ease");
            }
            if (animation.getAttribute("data-scroll")) {
                scroll = animation.getAttribute("data-scroll");
            }
            if (animation.getAttribute("data-offset")) {
                offset = animation.getAttribute("data-offset");
            }
            if (animation.getAttribute("data-split")) {
                split = animation.getAttribute("data-split");
            }
            if (scroll == 1) {
                if (type == "slide-up") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        yPercent: offset,
                        duration,
                        ease,
                        opacity: 0,
                        stagger: {
                            amount: stagger
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "slide-down") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        yPercent: -offset,
                        duration,
                        ease,
                        opacity: 0,
                        stagger: {
                            amount: stagger
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "rotate-in") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.set(animation.querySelectorAll(`.${split}`), {
                        transformPerspective: 400,
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        rotationX: -offset,
                        duration,
                        ease,
                        force3D: true,
                        opacity: 0,
                        transformOrigin: "top center -50",
                        stagger: {
                            amount: stagger
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "slide-from-left") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        xPercent: -offset,
                        duration,
                        opacity: 0,
                        ease,
                        stagger: {
                            amount: stagger
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "slide-from-right") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        xPercent: offset,
                        duration,
                        opacity: 0,
                        ease,
                        stagger: {
                            amount: stagger
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "fade-in") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        duration,
                        ease,
                        opacity: 0,
                        stagger: {
                            amount: stagger
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "fade-in-random") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        duration,
                        ease,
                        opacity: 0,
                        stagger: {
                            amount: stagger,
                            from: "random"
                        },
                    });
                    createScrollTrigger(animation, tl);
                }
                if (type == "scrub") {
                    let tl = gsap.timeline({
                        scrollTrigger: {
                            trigger: animation,
                            start: "top 90%",
                            end: "top center",
                            scrub: true,
                        },
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0.2,
                        duration,
                        ease,
                        stagger: {
                            amount: stagger
                        },
                    });
                }

                // Avoid flash of unstyled content
                gsap.set("[data-text-animation]", {
                    opacity: 1
                });
            } else {
                if (type == "slide-up") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        yPercent: offset,
                        duration,
                        ease,
                        opacity: 0,
                    });
                }
                if (type == "slide-down") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        yPercent: -offset,
                        duration,
                        ease,
                        opacity: 0,
                    });
                }
                if (type == "rotate-in") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.set(animation.querySelectorAll(`.${split}`), {
                        transformPerspective: 400,
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        rotationX: -offset,
                        duration,
                        ease,
                        force3D: true,
                        opacity: 0,
                        transformOrigin: "top center -50",
                    });
                }
                if (type == "slide-from-right") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        xPercent: offset,
                        duration,
                        opacity: 0,
                        ease,
                    });
                }
                if (type == "fade-in") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        duration,
                        ease,
                        opacity: 0,
                    });
                }
                if (type == "text-slide-effect") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        duration,
                        ease,
                        opacity: 0,
                    });
                }
                if (type == "fade-in-random") {
                    let tl = gsap.timeline({
                        paused: true
                    });
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0,
                        duration,
                        ease,
                        opacity: 0,
                        stagger: {
                            amount: stagger,
                            from: "random"
                        },
                    });
                }
                if (type == "scrub") {
                    tl.from(animation.querySelectorAll(`.${split}`), {
                        opacity: 0.2,
                        duration,
                        ease,
                    });
                }
            }
        });

        function textAnimationEffect() {
            let TextAnim = gsap.timeline();
            let splitText = new SplitType(".text-animation-effect", {
                types: 'chars'
            });
            if ($('.text-animation-effect .char').length) {
                TextAnim.from(".text-animation-effect .char", {
                    duration: 1,
                    x: 100,
                    autoAlpha: 0,
                    stagger: 0.1
                }, "-=1");
            }
        }

        window.addEventListener("load", (event) => {
            textAnimationEffect();
        });

        if ($(".fade-wrapper").length > 0) {
            $(".fade-wrapper").each(function() {
                var section = $(this);
                var fadeItems = section.find(".fade-top");

                fadeItems.each(function(index, element) {
                    var delay = index * 0.15;

                    gsap.set(element, {
                        opacity: 0,
                        y: 100,
                    });

                    ScrollTrigger.create({
                        trigger: element,
                        start: "top 100%",
                        end: "bottom 20%",
                        scrub: 0.5,
                        onEnter: function() {
                            gsap.to(element, {
                                opacity: 1,
                                y: 0,
                                duration: 1,
                                delay: delay,
                            });
                        },
                        once: true,
                    });
                });
            });
        }

        // index-3 : image about — entrée gauche + scale up au scroll (miroir de strength-man)
        (function() {
            if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
            var aboutImg = document.querySelector(".about-section-3 .about-img-slide-in");
            if (!aboutImg || typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") return;

            gsap.fromTo(
                aboutImg, {
                    xPercent: -30,
                    scale: 0.82,
                    opacity: 0
                }, {
                    xPercent: 0,
                    scale: 1,
                    opacity: 1,
                    duration: 2,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: aboutImg,
                        start: "top 85%",
                        toggleActions: "restart none none reset"
                    }
                }
            );
        })();

        // index-3 / sit_base : cartes promo — entrée gauche / bas / droite au scroll, sortie inverse
        (function() {
            if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                return;
            }
            if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
                return;
            }

            var section = document.querySelector("section.promo-section.pb-120");
            if (!section) {
                return;
            }

            var row = section.querySelector(".row.fade-wrapper");
            if (!row) {
                return;
            }

            var cols = Array.prototype.filter.call(row.children, function(el) {
                return el.matches && el.matches(".col-lg-4.col-md-6");
            });
            if (cols.length < 3) {
                return;
            }

            var leftCol = cols[0];
            var midCol = cols[1];
            var rightCol = cols[2];

            var distX = 160;
            var distY = 140;
            var durationIn = 1.45;
            var durationOut = 1.05;
            var easeIn = "power2.out";
            var easeOut = "power2.in";

            function setOffScreen() {
                gsap.set(leftCol, {
                    x: -distX,
                    y: 0,
                    opacity: 0,
                    overwrite: "auto"
                });
                gsap.set(midCol, {
                    x: 0,
                    y: distY,
                    opacity: 0,
                    overwrite: "auto"
                });
                gsap.set(rightCol, {
                    x: distX,
                    y: 0,
                    opacity: 0,
                    overwrite: "auto"
                });
            }

            function slideIn() {
                gsap.to(leftCol, {
                    x: 0,
                    y: 0,
                    opacity: 1,
                    duration: durationIn,
                    ease: easeIn,
                    overwrite: "auto"
                });
                gsap.to(midCol, {
                    x: 0,
                    y: 0,
                    opacity: 1,
                    duration: durationIn,
                    ease: easeIn,
                    delay: 0.22,
                    overwrite: "auto"
                });
                gsap.to(rightCol, {
                    x: 0,
                    y: 0,
                    opacity: 1,
                    duration: durationIn,
                    ease: easeIn,
                    delay: 0.44,
                    overwrite: "auto"
                });
            }

            function slideOut() {
                gsap.to(leftCol, {
                    x: -distX,
                    y: 0,
                    opacity: 0,
                    duration: durationOut,
                    ease: easeOut,
                    overwrite: "auto"
                });
                gsap.to(midCol, {
                    x: 0,
                    y: distY,
                    opacity: 0,
                    duration: durationOut,
                    ease: easeOut,
                    delay: 0.14,
                    overwrite: "auto"
                });
                gsap.to(rightCol, {
                    x: distX,
                    y: 0,
                    opacity: 0,
                    duration: durationOut,
                    ease: easeOut,
                    delay: 0.28,
                    overwrite: "auto"
                });
            }

            setOffScreen();

            ScrollTrigger.create({
                trigger: section,
                start: "top 88%",
                end: "bottom 12%",
                onEnter: slideIn,
                onEnterBack: slideIn,
                onLeave: slideOut,
                onLeaveBack: slideOut,
            });
        })();

        // index-3 : voiture section chiffres (entrée droite + scale up au scroll)
        (function() {
            if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
            var strengthCar = document.querySelector(".strength-section--index3-stack .strength-man");
            if (!strengthCar || typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") return;

            gsap.fromTo(
                strengthCar, {
                    xPercent: 30,
                    scale: 0.82,
                    opacity: 0
                }, {
                    xPercent: 0,
                    scale: 1,
                    opacity: 1,
                    duration: 2,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: strengthCar,
                        start: "top 85%",
                        toggleActions: "restart none none reset"
                    }
                }
            );
        })();

        // Page Scroll Percentage
        function scrollTopPercentage() {
            const scrollPercentage = () => {
                const scrollTopPos = document.documentElement.scrollTop;
                const calcHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrollValue = Math.round((scrollTopPos / calcHeight) * 100);
                const scrollElementWrap = $("#scroll-percentage");

                scrollElementWrap.css("background", `conic-gradient( var(--bz-color-theme-primary) ${scrollValue}%, var(--bz-color-common-white) ${scrollValue}%)`);

                // ScrollProgress
                if (scrollTopPos > 100) {
                    scrollElementWrap.addClass("active");
                } else {
                    scrollElementWrap.removeClass("active");
                }

                if (scrollValue < 96) {
                    $("#scroll-percentage-value").text(`${scrollValue}%`);
                } else {
                    $("#scroll-percentage-value").html('<i class="fa-sharp fa-regular fa-arrow-up-long"></i>');
                }
            }
            window.onscroll = scrollPercentage;
            window.onload = scrollPercentage;

            // Back to Top
            function scrollToTop() {
                document.documentElement.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            }

            $("#scroll-percentage").on("click", scrollToTop);
        }
        scrollTopPercentage();
    });




    $(".popup-image").magnificPopup({
        type: "image",
        gallery: {
            enabled: true,
        },
    });

    // testimonial-4__active start
    var testimonial = new Swiper('.testimonial-4__active', {
        slidesPerView: 3,
        loop: true,
        autoplay: true,
        arrow: true,
        spaceBetween: 30,
        speed: 1500,
        centeredSlides: true,
        pagination: {
            el: ".testimonial-4__pagination",
            clickable: true,
        },
        breakpoints: {
            320: {
                slidesPerView: 1,
            },
            575: {
                slidesPerView: 2,
                centeredSlides: false,
                spaceBetween: 20,
            },
            767: {
                slidesPerView: 2,
            },
            1200: {
                slidesPerView: 3,
            },
        },
    });

    // feedback-5__active start
    var services = new Swiper('.feedback-5__active', {
        slidesPerView: 2,
        loop: true,
        autoplay: true,
        arrow: false,
        spaceBetween: 30,
        speed: 1500,
        centeredSlides: false,
        breakpoints: {
            320: {
                slidesPerView: 1,
            },
            575: {
                slidesPerView: 2,
            },
            992: {
                slidesPerView: 2,
            },
            1200: {
                slidesPerView: 2,
            },
        },
    });

    // project-5__active start
    var project_5__active = new Swiper(".project-5__active", {
        spaceBetween: 1,
        slidesPerView: 3,
        centeredSlides: true,
        roundLengths: true,
        loop: true,
        autoplay: true,
        speed: 1500,
        loopAdditionalSlides: 30,

        breakpoints: {
            320: {
                slidesPerView: 1,
            },
            575: {
                slidesPerView: 1,
            },
            993: {
                slidesPerView: 2,
            },
            1200: {
                slidesPerView: 3,
            },
        },
    });

    //client-testimonial start
    $(function() {
        var galleryTop, galleryThumbs;

        function initSwiper() {
            // Destroy existing Swiper instances if they exist
            if (galleryTop) {
                galleryTop.destroy(true, true);
            }
            if (galleryThumbs) {
                galleryThumbs.destroy(true, true);
            }

            // Check if the required elements exist
            if ($(".mySwiperDesktop").length || $(".mySwiper").length || $(".mySwiper2").length) {
                if ($(window).width() > 768) {
                    // Initialize Swiper for desktop
                    galleryTop = new Swiper(".mySwiperDesktop", {
                        spaceBetween: 10,
                        slidesPerView: 9,
                        direction: 'horizontal', // Default slides per view for desktop
                        centeredSlides: true,
                        loop: true,
                        watchSlidesProgress: true,
                        breakpoints: {
                            320: {
                                slidesPerView: 1
                            },
                            575: {
                                slidesPerView: 5
                            },
                            993: {
                                slidesPerView: 7
                            },
                            1200: {
                                slidesPerView: 9
                            },
                        },
                    });
                    galleryThumbs = new Swiper(".mySwiper2", {
                        spaceBetween: 10,
                        navigation: {
                            nextEl: ".swiper-button-next",
                            prevEl: ".swiper-button-prev",
                        },
                        a11y: {
                            prevSlideMessage: "Previous slide",
                            nextSlideMessage: "Next slide",
                        },
                        thumbs: {
                            swiper: galleryTop
                        },
                    });
                } else {
                    // Initialize Swiper for mobile
                    galleryTop = new Swiper(".mySwiper", {
                        spaceBetween: 10,
                        slidesPerView: 9,
                        freeMode: false,
                        centeredSlides: true,
                        loop: true,
                        watchSlidesProgress: true,
                        breakpoints: {
                            320: {
                                slidesPerView: 3
                            },
                            575: {
                                slidesPerView: 4
                            },
                            993: {
                                slidesPerView: 7
                            },
                            1200: {
                                slidesPerView: 9
                            },
                        },
                    });
                    galleryThumbs = new Swiper(".mySwiper2", {
                        spaceBetween: 10,
                        navigation: {
                            nextEl: ".swiper-button-next",
                            prevEl: ".swiper-button-prev",
                        },
                        a11y: {
                            prevSlideMessage: "Previous slide",
                            nextSlideMessage: "Next slide",
                        },
                        thumbs: {
                            swiper: galleryTop
                        },
                    });
                }

                // Sync the slide change between galleryTop and galleryThumbs
                galleryTop.on("slideChangeTransitionStart", function() {
                    galleryThumbs.slideTo(galleryTop.activeIndex);
                });
                galleryThumbs.on("transitionStart", function() {
                    galleryTop.slideTo(galleryThumbs.activeIndex);
                });
            }
        }

        initSwiper();

        // Reinitialize Swiper on window resize
        $(window).resize(function() {
            initSwiper();
        });
    });


    document.addEventListener("DOMContentLoaded", () => {
        const boxes = document.querySelectorAll(".project-thumb");

        boxes.forEach((box) => {
            box.addEventListener("mouseover", () => {
                // Remove 'active' class from all boxes
                boxes.forEach((item) => item.classList.remove("active"));

                // Add 'active' class to the clicked box
                box.classList.add("active");
            });
        });
    });

    // index-3 : animation footer waves rouges (2 vagues, très transparent)
    document.addEventListener("DOMContentLoaded", () => {
        const footerWaveRoot = document.querySelector(".footer-wave--index3 .footer-wave-svg--index3");
        if (!footerWaveRoot || typeof gsap === "undefined") return;

        const svg = footerWaveRoot;
        const waveGroups = svg.querySelectorAll(".g");
        if (!waveGroups.length) return;

        const animateGroup = ($el) => {
            const $paths = $el.querySelectorAll(".path");
            if (!$paths.length) return;

            const tl = gsap.timeline();
            const duration = gsap.utils.random(18, 32);
            const y = gsap.utils.random(-22, 22);
            const rotate = gsap.utils.random(-6, 6);

            const scaleXFrom = gsap.utils.random(1.15, 1.25);
            const scaleXTo = gsap.utils.random(1.0, 1.15);
            const scaleYFrom = gsap.utils.random(0.9, 1.05);
            const scaleYTo = gsap.utils.random(0.7, 0.85);

            // Presque transparent (subtil)
            const opacityFrom = gsap.utils.random(0.06, 0.12);
            const opacityTo = gsap.utils.random(0.08, 0.16);

            const ease = gsap.utils.random(["power2.inOut", "power3.inOut", "sine.inOut"]);

            tl.to($paths, {
                xPercent: -120,
                duration,
                ease: "none",
                repeat: -1,
            });

            tl.fromTo(
                $el, {
                    y,
                    opacity: opacityFrom,
                    rotate,
                    scaleY: scaleYFrom,
                    scaleX: scaleXFrom,
                    transformOrigin: "50% 50%",
                }, {
                    y: y * -1,
                    opacity: opacityTo,
                    rotate: rotate * -1,
                    scaleY: scaleYTo,
                    scaleX: scaleXTo,
                    repeat: -1,
                    yoyo: true,
                    yoyoEase: ease,
                    duration: duration * 0.22,
                    ease: ease,
                    transformOrigin: "50% 50%",
                },
                0
            );

            tl.seek(gsap.utils.random(2, 12));
        };

        waveGroups.forEach((groupEl) => animateGroup(groupEl));
        gsap.to(svg, {
            opacity: 1,
            duration: 0.7
        });
    });

})(jQuery);