// ==UserScript==
// @name            Nyaa Magnet Links
// @match           https://*.nyaa.si/
// @version         1.1
// @description     Gather all magnet links in one page and copy them to clipboard.
// @icon            https://nyaa.si/static/favicon.png
// @run-at          document-end
// ==/UserScript==

async function getLinks() {
    // Retrieves all magnet links and copies them to clipboard.
    let links = Array
        .from(document.querySelectorAll("a"))
        .filter(a => a.href.startsWith("magnet:"))
        .map(a => a.href)
        .join("\n");
    await navigator.clipboard.writeText(links);

    let note = document.createElement("div");
    note.classList.add("alert", "alert-info");
    note.textContent = "Magnet links copied to clipboard";

    document.querySelectorAll(".container")[1].prepend(note);
}

// Add an extra button beside search for copying the links.
let div = document.createElement("div");
div.classList.add("btn", "btn-primary");
let i = document.createElement("i");
i.classList.add("fa", "fa-magnet", "fa-fw");
div.append(i);
div.addEventListener("click", getLinks);
document.querySelectorAll(".navbar-form")[1].append(div);
