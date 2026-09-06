/**
* Theme: Larkon - Responsive Bootstrap 5 Admin Dashboard
* Author: Techzaa
* Module/App: Theme Layout Customizer Js
*/

class ThemeLayout {

     constructor() {
          this.html = document.getElementsByTagName('html')[0]
          this.config = window.config;
     }

     // Main Nav
     initVerticalMenu() {
          const navCollapse = document.querySelectorAll('.navbar-nav li .collapse');
          const navToggle = document.querySelectorAll(".navbar-nav li [data-bs-toggle='collapse']");

          navToggle.forEach(toggle => {
               toggle.addEventListener('click', function (e) {
                    e.preventDefault();
               });
          });

          // open one menu at a time only (Auto Close Menu)
          navCollapse.forEach(collapse => {
               collapse.addEventListener('show.bs.collapse', function (event) {
                    const parent = event.target.closest('.collapse.show');
                    document.querySelectorAll('.navbar-nav .collapse.show').forEach(element => {
                         if (element !== event.target && element !== parent) {
                              const collapseInstance = new bootstrap.Collapse(element);
                              collapseInstance.hide();
                         }
                    });
               });
          });

          if (document.querySelector(".navbar-nav")) {
               // Activate the menu in left side bar based on url
               document.querySelectorAll(".navbar-nav a").forEach(function (link) {
                    var pageUrl = window.location.href.split(/[?#]/)[0];

                    if (link.href === pageUrl) {
                         link.classList.add("active");
                         link.parentNode.classList.add("active");

                         let parentCollapseDiv = link.closest(".collapse");
                         while (parentCollapseDiv) {
                              parentCollapseDiv.classList.add("show");
                              parentCollapseDiv.parentElement.children[0].classList.add("active");
                              parentCollapseDiv.parentElement.children[0].setAttribute("aria-expanded", "true");
                              parentCollapseDiv = parentCollapseDiv.parentElement.closest(".collapse");
                         }
                    }
               });

               setTimeout(function () {
                    var activatedItem = document.querySelector('li a.active');

                    if (activatedItem != null) {
                         var simplebarContent = document.querySelector('.main-nav .simplebar-content-wrapper');
                         var offset = activatedItem.offsetTop - 300;
                         if (simplebarContent && offset > 100) {
                              scrollTo(simplebarContent, offset, 600);
                         }
                    }
               }, 200);

               // scrollTo (Left Side Bar Active Menu)
               function easeInOutQuad(t, b, c, d) {
                    t /= d / 2;
                    if (t < 1) return c / 2 * t * t + b;
                    t--;
                    return -c / 2 * (t * (t - 2) - 1) + b;
               }

               function scrollTo(element, to, duration) {
                    var start = element.scrollTop, change = to - start, currentTime = 0, increment = 20;
                    var animateScroll = function () {
                         currentTime += increment;
                         var val = easeInOutQuad(currentTime, start, change, duration);
                         element.scrollTop = val;
                         if (currentTime < duration) {
                              setTimeout(animateScroll, increment);
                         }
                    };
                    animateScroll();
               }
          }
     }

     initSidebarHover() {
          var self = this;
          var mainNav = document.querySelector('.main-nav');
          if (!mainNav) return;

          var hoverTimer = null;
          var HOVER_DELAY = 1500; // 1.5 seconds delay

          mainNav.addEventListener('mouseenter', function () {
               var currentSize = self.html.getAttribute('data-menu-size');
               if (currentSize === 'sm-hover' && window.innerWidth >= 992) {
                    if (hoverTimer) clearTimeout(hoverTimer);
                    hoverTimer = setTimeout(function () {
                         mainNav.classList.add('hover-expanded');
                    }, HOVER_DELAY);
               }
          });

          mainNav.addEventListener('mouseleave', function () {
               if (hoverTimer) {
                    clearTimeout(hoverTimer);
                    hoverTimer = null;
               }
               mainNav.classList.remove('hover-expanded');
          });
     }

     initConfig() {
          this.config = JSON.parse(JSON.stringify(window.config));
          this.setSwitchFromConfig();
     }

     changeMenuColor(color) {
          this.config.menu.color = color;
          this.html.setAttribute('data-menu-color', color);
          this.setSwitchFromConfig();
     }

     changeMenuSize(size, save = true) {
          this.html.setAttribute('data-menu-size', size);
          if (save) {
               this.config.menu.size = size;
               this.setSwitchFromConfig();
          }
     }

     changeThemeMode(color) {
          this.config.theme = color;
          this.html.setAttribute('data-bs-theme', color);
          this.setSwitchFromConfig();
     }

     changeTopbarColor(color) {
          this.config.topbar.color = color;
          this.html.setAttribute('data-topbar-color', color);
          this.setSwitchFromConfig();
     }

     resetTheme() {
          this.config = JSON.parse(JSON.stringify(window.defaultConfig));
          this.changeMenuColor(this.config.menu.color);
          this.changeMenuSize(this.config.menu.size);
          this.changeThemeMode(this.config.theme);
          this.changeTopbarColor(this.config.topbar.color);
     }

     initSwitchListener() {
          var self = this;
          document.querySelectorAll('input[name=data-menu-color]').forEach(function (element) {
               element.addEventListener('change', function (e) {
                    self.changeMenuColor(element.value);
               })
          });

          document.querySelectorAll('input[name=data-menu-size]').forEach(function (element) {
               element.addEventListener('change', function (e) {
                    self.changeMenuSize(element.value);
               })
          });

          document.querySelectorAll('input[name=data-bs-theme]').forEach(function (element) {
               element.addEventListener('change', function (e) {
                    self.changeThemeMode(element.value);
               })
          });

          document.querySelectorAll('input[name=data-topbar-color]').forEach(function (element) {
               element.addEventListener('change', function (e) {
                    self.changeTopbarColor(element.value);
               })
          });

          //TopBar Light Dark
          var themeColorToggle = document.getElementById('light-dark-mode');
          if (themeColorToggle) {
               themeColorToggle.addEventListener('click', function (e) {
                    if (self.config.theme === 'light') {
                         self.changeThemeMode('dark');
                    } else {
                         self.changeThemeMode('light');
                    }
               });
          }

          var resetBtn = document.querySelector('#reset-layout')
          if (resetBtn) {
               resetBtn.addEventListener('click', function (e) {
                    self.resetTheme();
               });
          }

          // Menu toggle buttons (Topbar & Mobile Bottom Bar)
          document.querySelectorAll('.button-toggle-menu').forEach(function (btn) {
               btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    if (window.innerWidth >= 992) {
                         var currentSize = self.html.getAttribute('data-menu-size');
                         if (currentSize === 'default') {
                              self.changeMenuSize('sm-hover', true);
                              localStorage.setItem("__GRIFE_HF_SIDEBAR_PINNED__", "false");
                         } else {
                              self.changeMenuSize('default', true);
                              localStorage.setItem("__GRIFE_HF_SIDEBAR_PINNED__", "true");
                         }
                    } else {
                         self.toggleMobileSidebar();
                    }
               });
          });

          // Mobile Drawer Close Button (X)
          var closeMobileBtn = document.getElementById('btn-close-sidebar-mobile');
          if (closeMobileBtn) {
               closeMobileBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    self.closeMobileSidebar();
               });
          }

          // Desktop Sidebar Pin Button (📌)
          var pinDesktopBtn = document.getElementById('btn-pin-sidebar-desktop');
          if (pinDesktopBtn) {
               pinDesktopBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var currentSize = self.html.getAttribute('data-menu-size');
                    if (currentSize === 'default') {
                         self.changeMenuSize('sm-hover', true);
                         localStorage.setItem("__GRIFE_HF_SIDEBAR_PINNED__", "false");
                    } else {
                         self.changeMenuSize('default', true);
                         localStorage.setItem("__GRIFE_HF_SIDEBAR_PINNED__", "true");
                    }
                    var mainNav = document.querySelector('.main-nav');
                    if (mainNav) mainNav.classList.remove('hover-expanded');
               });
          }

          var hoverBtn = document.querySelectorAll('.button-sm-hover');
          hoverBtn.forEach(function (element) {
               element.addEventListener('click', function () {
                    var configSize = self.config.menu.size;
                    var size = self.html.getAttribute('data-menu-size', configSize);

                    if (configSize === 'sm-hover-active') {
                         if (size === 'sm-hover-active') {
                              self.changeMenuSize('sm-hover', true);
                         } else {
                              self.changeMenuSize('sm-hover-active', true);
                         }
                    }

                    if (configSize === 'sm-hover') {
                         if (size === 'sm-hover') {
                              self.changeMenuSize('sm-hover-active', true);
                         } else {
                              self.changeMenuSize('sm-hover', true);
                         }
                    }
               });
          })
     }

     toggleMobileSidebar() {
          this.html.classList.toggle('sidebar-enable');
          if (this.html.classList.contains('sidebar-enable')) {
               this.showBackdrop();
          } else {
               this.closeMobileSidebar();
          }
     }

     closeMobileSidebar() {
          this.html.classList.remove('sidebar-enable');
          var backdrop = document.querySelector('.offcanvas-backdrop');
          if (backdrop) {
               backdrop.remove();
          }
          document.body.style.overflow = null;
          document.body.style.paddingRight = null;
     }

     showBackdrop() {
          var backdrop = document.querySelector('.offcanvas-backdrop');
          if (!backdrop) {
               backdrop = document.createElement('div');
               backdrop.className = 'offcanvas-backdrop fade show';
               document.body.appendChild(backdrop);
          }
          document.body.style.overflow = "hidden";
          if (window.innerWidth > 1040) {
               document.body.style.paddingRight = "15px";
          }
          var self = this;
          backdrop.addEventListener('click', function (e) {
               self.closeMobileSidebar();
          });
     }

     initTouchGestures() {
          var self = this;
          var touchStartX = 0;
          var touchStartY = 0;
          var touchEndX = 0;
          var touchEndY = 0;

          document.addEventListener('touchstart', function (e) {
               touchStartX = e.changedTouches[0].screenX;
               touchStartY = e.changedTouches[0].screenY;
          }, { passive: true });

          document.addEventListener('touchend', function (e) {
               touchEndX = e.changedTouches[0].screenX;
               touchEndY = e.changedTouches[0].screenY;

               var diffX = touchEndX - touchStartX;
               var diffY = Math.abs(touchEndY - touchStartY);

               // Only trigger on horizontal swipe
               if (diffY < 60 && window.innerWidth < 992) {
                    // Swipe right from left edge (< 40px) to open sidebar
                    if (touchStartX < 40 && diffX > 60) {
                         if (!self.html.classList.contains('sidebar-enable')) {
                              self.toggleMobileSidebar();
                         }
                    }
                    // Swipe left when sidebar is open to close it
                    else if (self.html.classList.contains('sidebar-enable') && diffX < -60) {
                         self.closeMobileSidebar();
                    }
               }
          }, { passive: true });
     }

     initKeyboardShortcuts() {
          var self = this;
          document.addEventListener('keydown', function (e) {
               // Ctrl + B or Cmd + B
               if ((e.ctrlKey || e.metaKey) && (e.key === 'b' || e.key === 'B')) {
                    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
                    e.preventDefault();

                    if (window.innerWidth >= 992) {
                         var currentSize = self.html.getAttribute('data-menu-size');
                         if (currentSize === 'default') {
                              self.changeMenuSize('sm-hover', true);
                              localStorage.setItem("__GRIFE_HF_SIDEBAR_PINNED__", "false");
                         } else {
                              self.changeMenuSize('default', true);
                              localStorage.setItem("__GRIFE_HF_SIDEBAR_PINNED__", "true");
                         }
                         var mainNav = document.querySelector('.main-nav');
                         if (mainNav) mainNav.classList.remove('hover-expanded');
                    } else {
                         self.toggleMobileSidebar();
                    }
               }
          });
     }

     initWindowSize() {
          var self = this;
          window.addEventListener('resize', function (e) {
               self._adjustLayout();
          })
     }

     _adjustLayout() {
          var self = this;

          if (window.innerWidth < 992) {
               self.changeMenuSize('hidden', false);
          } else {
               var isPinned = localStorage.getItem("__GRIFE_HF_SIDEBAR_PINNED__") === "true";
               self.changeMenuSize(isPinned ? 'default' : 'sm-hover', false);
          }
     }

     setSwitchFromConfig() {

          sessionStorage.setItem('__LARKON_CONFIG__', JSON.stringify(this.config));

          document.querySelectorAll('.settings-bar input[type=radio]').forEach(function (checkbox) {
               checkbox.checked = false;
          })

          var config = this.config;
          if (config) {
               var layoutColorSwitch = document.querySelector('input[type=radio][name=data-bs-theme][value=' + config.theme + ']');
               var topbarColorSwitch = document.querySelector('input[type=radio][name=data-topbar-color][value=' + config.topbar.color + ']');
               var leftbarSizeSwitch = document.querySelector('input[type=radio][name=data-menu-size][value=' + config.menu.size + ']');
               var leftbarColorSwitch = document.querySelector('input[type=radio][name=data-menu-color][value=' + config.menu.color + ']');

               if (layoutColorSwitch) layoutColorSwitch.checked = true;
               if (topbarColorSwitch) topbarColorSwitch.checked = true;
               if (leftbarSizeSwitch) leftbarSizeSwitch.checked = true;
               if (leftbarColorSwitch) leftbarColorSwitch.checked = true;
          }
     }

     init() {
          this.initVerticalMenu();
          this.initSidebarHover();
          this.initConfig();
          this.initSwitchListener();
          this.initTouchGestures();
          this.initKeyboardShortcuts();
          this.initWindowSize();
          this._adjustLayout();
          this.setSwitchFromConfig();
     }
}

new ThemeLayout().init();