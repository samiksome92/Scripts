// ==UserScript==
// @name         Desktop Wikipedia Redirect
// @description  Redirect mobile wikipedia pages to desktop version.
// @icon         https://en.wikipedia.org/static/favicon/wikipedia.ico
// @author       samiksome92
// @version      1.1
// @match        *://*.m.wikipedia.org/*
// @run-at       document-start
// ==/UserScript==

const url = new URL(window.location.href);
const language = url.hostname.split('.')[0];
const desktopWikipedia = "https://" + language + ".wikipedia.org";

if (url.hostname.indexOf(".m.") === -1)
    return;

window.location.replace(desktopWikipedia + url.pathname + url.search + url.hash);
