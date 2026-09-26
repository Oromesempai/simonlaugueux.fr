// Menu mobile et apparition des sections au scroll.
// Le site reste entièrement utilisable sans ce script.
(function () {
  document.documentElement.classList.add("js");

  var bouton = document.querySelector(".nav-toggle");
  var menu = document.getElementById("menu");

  function basculerMenu(ouvert) {
    bouton.setAttribute("aria-expanded", String(ouvert));
    menu.classList.toggle("ouvert", ouvert);
  }

  if (bouton && menu) {
    bouton.addEventListener("click", function () {
      basculerMenu(bouton.getAttribute("aria-expanded") !== "true");
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("a")) {
        basculerMenu(false);
      }
    });
  }

  var sections = document.querySelectorAll(".reveal");
  var mouvementReduit = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function toutAfficher() {
    for (var i = 0; i < sections.length; i++) sections[i].classList.add("visible");
  }

  if (mouvementReduit || !window.IntersectionObserver) {
    toutAfficher();
    return;
  }

  // En cas d'échec, mieux vaut tout afficher que laisser des sections invisibles.
  try {
    var observateur = new window.IntersectionObserver(function (entrees) {
      entrees.forEach(function (entree) {
        if (entree.isIntersecting) {
          entree.target.classList.add("visible");
          observateur.unobserve(entree.target);
        }
      });
    }, { rootMargin: "0px 0px -10% 0px" });

    for (var i = 0; i < sections.length; i++) observateur.observe(sections[i]);
  } catch (e) {
    toutAfficher();
  }
})();
