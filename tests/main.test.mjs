// Test du comportement de assets/js/main.js avec un faux DOM minimal.
// Lancer : node --test tests/main.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const code = readFileSync(new URL("../assets/js/main.js", import.meta.url), "utf8");

class FakeClassList {
  constructor() { this.noms = new Set(); }
  add(n) { this.noms.add(n); }
  remove(n) { this.noms.delete(n); }
  contains(n) { return this.noms.has(n); }
  toggle(n, force) {
    const actif = force === undefined ? !this.noms.has(n) : force;
    if (actif) this.noms.add(n); else this.noms.delete(n);
    return actif;
  }
}

class FakeElement {
  constructor(tag, parent = null) {
    this.tagName = tag.toUpperCase();
    this.parent = parent;
    this.classList = new FakeClassList();
    this.attrs = {};
    this.listeners = {};
  }
  getAttribute(n) { return n in this.attrs ? this.attrs[n] : null; }
  setAttribute(n, v) { this.attrs[n] = String(v); }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  dispatch(type, target = this) { (this.listeners[type] || []).forEach((fn) => fn({ target })); }
  closest(sel) {
    for (let el = this; el; el = el.parent) {
      if (el.tagName === sel.toUpperCase()) return el;
    }
    return null;
  }
}

function charger({ mouvementReduit = false, observer = true, observerCasse = false } = {}) {
  const racine = new FakeElement("html");
  const bouton = new FakeElement("button");
  bouton.setAttribute("aria-expanded", "false");
  const menu = new FakeElement("ul");
  const lien = new FakeElement("a", new FakeElement("li", menu));
  const reveals = [new FakeElement("section"), new FakeElement("section")];
  const observes = [];
  let rappel = null;

  const document = {
    documentElement: racine,
    querySelector: (s) => (s === ".nav-toggle" ? bouton : null),
    getElementById: (id) => (id === "menu" ? menu : null),
    querySelectorAll: (s) => (s === ".reveal" ? reveals : []),
  };
  const window = { matchMedia: () => ({ matches: mouvementReduit }) };
  if (observer) {
    window.IntersectionObserver = class {
      constructor(cb) {
        if (observerCasse) throw new Error("observateur indisponible");
        rappel = cb;
      }
      observe(el) { observes.push(el); }
      unobserve(el) { observes.splice(observes.indexOf(el), 1); }
    };
  }
  vm.runInNewContext(code, { document, window });
  return { racine, bouton, menu, lien, reveals, observes, declencher: (entries) => rappel(entries) };
}

test("pose la classe js sur <html>", () => {
  assert.ok(charger().racine.classList.contains("js"));
});

test("le bouton ouvre puis referme le menu", () => {
  const { bouton, menu } = charger();
  bouton.dispatch("click");
  assert.equal(bouton.getAttribute("aria-expanded"), "true");
  assert.ok(menu.classList.contains("ouvert"));
  bouton.dispatch("click");
  assert.equal(bouton.getAttribute("aria-expanded"), "false");
  assert.ok(!menu.classList.contains("ouvert"));
});

test("cliquer un lien du menu referme le menu", () => {
  const { bouton, menu, lien } = charger();
  bouton.dispatch("click");
  menu.dispatch("click", lien);
  assert.equal(bouton.getAttribute("aria-expanded"), "false");
  assert.ok(!menu.classList.contains("ouvert"));
});

test("cliquer dans le menu hors d'un lien ne le referme pas", () => {
  const { bouton, menu } = charger();
  bouton.dispatch("click");
  menu.dispatch("click", menu);
  assert.equal(bouton.getAttribute("aria-expanded"), "true");
});

test("les sections apparaissent à l'entrée dans le viewport", () => {
  const { reveals, observes, declencher } = charger();
  assert.equal(observes.length, 2);
  assert.ok(!reveals[0].classList.contains("visible"));
  declencher([
    { isIntersecting: true, target: reveals[0] },
    { isIntersecting: false, target: reveals[1] },
  ]);
  assert.ok(reveals[0].classList.contains("visible"));
  assert.ok(!reveals[1].classList.contains("visible"));
  assert.deepEqual(observes, [reveals[1]]);
});

test("mouvement réduit : tout est visible d'emblée, rien n'est observé", () => {
  const { reveals, observes } = charger({ mouvementReduit: true });
  assert.ok(reveals.every((el) => el.classList.contains("visible")));
  assert.equal(observes.length, 0);
});

test("sans IntersectionObserver : tout est visible d'emblée", () => {
  const { reveals } = charger({ observer: false });
  assert.ok(reveals.every((el) => el.classList.contains("visible")));
});

test("si l'observateur plante : tout est visible et aucune erreur ne remonte", () => {
  const { reveals } = charger({ observerCasse: true });
  assert.ok(reveals.every((el) => el.classList.contains("visible")));
});
