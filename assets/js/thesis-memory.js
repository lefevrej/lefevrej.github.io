/* Illustrative models from thesis Figures 4.11(a) and 6.4(a).
 * These estimates are not general capacity guarantees. */
(function () {
  "use strict";
  var root = document.querySelector("[data-thesis-memory]");
  if (!root) return;
  var locale = root.getAttribute("data-locale") === "fr" ? "fr" : "en";
  var french = locale === "fr";
  var strings = french ? {
    gb: "Go", mb: "Mo", million: "millions", billion: "milliards"
  } : {
    gb: "GB", mb: "MB", million: "million", billion: "billion"
  };

  if (french) {
    var chromeObserver;
    function localizeArticleLabels() {
      var labels = { authors: "Auteur", affiliations: "Affiliation", published: "Publié le" };
      var headings = document.querySelectorAll("d-byline h3");
      headings.forEach(function (heading) {
        var replacement = labels[heading.textContent.trim().toLowerCase()];
        if (replacement) heading.textContent = replacement;
      });
      var publishedHeading = Array.from(headings).find(function (heading) {
        return heading.textContent === "Publié le";
      });
      var metadata = document.querySelector("d-front-matter script");
      if (publishedHeading && publishedHeading.nextElementSibling && metadata) {
        var published = new Date(JSON.parse(metadata.textContent).published);
        if (!Number.isNaN(published.getTime())) {
          var dateLabel = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "long", year: "numeric" }).format(published);
          if (publishedHeading.nextElementSibling.textContent !== dateLabel) {
            publishedHeading.nextElementSibling.textContent = dateLabel;
          }
        }
      }
      var references = document.querySelector("d-appendix #references");
      if (references && references.textContent !== "Références") references.textContent = "Références";
      if (references && headings.length >= 3 && chromeObserver) chromeObserver.disconnect();
    }
    chromeObserver = new MutationObserver(localizeArticleLabels);
    [document.querySelector("d-byline"), document.querySelector("d-appendix")].forEach(function (element) {
      if (element) chromeObserver.observe(element, { childList: true, subtree: true });
    });
    localizeArticleLabels();
  }

  var total = root.querySelector("#memory-total");
  var outputs = {
    budget: root.querySelector("[data-memory-budget]"),
    incore: root.querySelector("[data-memory-incore]"),
    incoreVoxels: root.querySelector("[data-memory-incore-voxels]"),
    qfz: root.querySelector("[data-memory-qfz]"),
    qfzVoxels: root.querySelector("[data-memory-qfz-voxels]")
  };

  function format(value, digits) {
    return new Intl.NumberFormat(locale, { maximumFractionDigits: digits }).format(value);
  }

  function size(gb) {
    return gb < 1 ? format(gb * 1000, 0) + " " + strings.mb : format(gb, 1) + " " + strings.gb;
  }

  function voxels(gb) {
    return gb < 1 ? format(gb * 1000, 0) + " " + strings.million : format(gb, 1) + " " + strings.billion;
  }

  function update() {
    var budget = total.valueAsNumber;
    var inCore = Math.max(0, (budget - 0.062) / 162.94);
    var qfz = budget / 3;
    outputs.budget.textContent = format(budget, 0) + " " + strings.gb;
    total.setAttribute("aria-valuetext", outputs.budget.textContent);
    outputs.incore.textContent = size(inCore);
    outputs.incoreVoxels.textContent = voxels(inCore);
    outputs.qfz.textContent = size(qfz);
    outputs.qfzVoxels.textContent = voxels(qfz);
  }

  total.addEventListener("input", update);
  update();
}());
