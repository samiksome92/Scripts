// ==UserScript==
// @name         Nyaa Magnet Links
// @description  Gather all magnet links in one page of nyaa.si.
// @icon         https://nyaa.si/static/favicon.png
// @author       samiksome92
// @version      1.0
// @match        *://nyaa.si/
// @run-at       document-end
// ==/UserScript==

async function getLinks() {
    /**
     * Retrieves all magnet links in the page and copies them to the clipboard.
     * 
     * @returns Nothing.
     */
    let magnets = document.getElementsByClassName("fa-magnet");
    magnets = Array.from(magnets).slice(1); // Slice out first element since it corresponds to the added button.

    let allLinks = "";
    magnets.forEach(magnet => {
        magnet = magnet.parentElement.getAttribute("href");
        allLinks += magnet + "\n";
    });

    // Copy to clipboard.
    await navigator.clipboard.writeText(allLinks);

    // Show info alert.
    let template = document.createElement("template");
    const infoHTML = '<div class="alert alert-info">' +
        "Magnet links copied to clipboard" +
        "</div>"
    template.innerHTML = infoHTML;

    document.getElementsByClassName("container")[1].prepend(template.content.firstChild);
}

// Create template for an extra button beside search for gathering the links.
let template = document.createElement("template");
const buttonHTML = '<div class="input-group-btn">' +
    '<button id="getlinks-button" class="btn btn-primary" type="button">' +
    '<i class="fa fa-magnet fa-fw"></i>' +
    "</button></div>";
template.innerHTML = buttonHTML;

// Add the new button and attach listener for click.
document.getElementsByClassName("input-group")[0].append(template.content.firstChild);
document.getElementById("getlinks-button").addEventListener("click", getLinks);
