// ==UserScript==
// @name         Old Reddit Redirect
// @description  Redirect reddit to old.reddit.
// @icon         https://raw.githubusercontent.com/tom-james-watson/old-reddit-redirect/master/img/icon48.png
// @author       samiksome92
// @version      1.1
// @match        *://reddit.com/*
// @match        *://www.reddit.com/*
// @match        *://np.reddit.com/*
// @match        *://amp.reddit.com/*
// @match        *://i.reddit.com/*
// @run-at       document-start
// ==/UserScript==

// This is simply a user script variant of the extension Old Reddit Redirect by Tom Watson.
// GitHub link of the extension: https://github.com/tom-james-watson/old-reddit-redirect

const oldReddit = "https://old.reddit.com";
const excludedPaths = ["/gallery", "/poll", "/rpan", "/settings", "/topics", "/community-points"];
const url = new URL(window.location.href);

if (url.hostname === "old.reddit.com")
    return;

for (const path of excludedPaths) {
    if (url.pathname.indexOf(path) === 0)
        return;
}

window.location.replace(oldReddit + url.pathname + url.search + url.hash);
