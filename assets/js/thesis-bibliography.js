(() => {
  const selector = 'd-citation-list[data-thesis-reference-keys]';

  const groupReferences = (citationList) => {
    const thesisKeys = new Set(
      citationList.dataset.thesisReferenceKeys.split(',').map((key) => key.trim()).filter(Boolean)
    );
    const sourceList = citationList.querySelector(':scope > ol.references');

    if (!sourceList || sourceList.querySelector(':scope > .thesis-reference-heading')) return;

    const entries = Array.from(sourceList.children).filter((entry) => entry.tagName === 'LI');
    if (!entries.length) return;

    const groups = [
      {
        heading: citationList.dataset.thesisWorksHeading || 'Work directly resulting from the thesis',
        entries: entries.filter((entry) => thesisKeys.has(entry.id)),
      },
      {
        heading: citationList.dataset.externalReferencesHeading || 'External references',
        entries: entries.filter((entry) => !thesisKeys.has(entry.id)),
      },
    ];

    citationList.classList.add('thesis-reference-groups');
    sourceList.innerHTML = '';

    groups.forEach((group) => {
      if (!group.entries.length) return;

      const headingItem = document.createElement('li');
      headingItem.className = 'thesis-reference-heading';
      const heading = document.createElement('h4');
      heading.textContent = group.heading;
      headingItem.appendChild(heading);
      sourceList.appendChild(headingItem);

      group.entries.forEach((entry) => {
        entry.value = entries.indexOf(entry) + 1;
        sourceList.appendChild(entry);
      });
    });
  };

  const observeCitationList = (citationList) => {
    const observer = new MutationObserver(() => groupReferences(citationList));
    observer.observe(citationList, { childList: true, subtree: true });
    groupReferences(citationList);
  };

  const start = () => document.querySelectorAll(selector).forEach(observeCitationList);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
})();
