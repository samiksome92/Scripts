// ==UserScript==
// @name         Twitter Original Image Redirect
// @description  Redirect twitter images to show the original.
// @icon         https://abs.twimg.com/favicons/twitter.ico
// @author       samiksome92
// @version      1.0
// @match        *://pbs.twimg.com/media/*
// @run-at       document-start
// ==/UserScript==

const url = window.location.href;

if (url.endsWith("=orig"))
    return;

const idx = url.lastIndexOf("=");
const originalUrl = url.substring(0, idx) + "=orig";

window.location.replace(originalUrl);
