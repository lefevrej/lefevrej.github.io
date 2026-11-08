/* Linked partitions and inclusion trees, reconstructed from retained UCMs. */
(() => {
  'use strict';
  const palette = [[53, 161, 224], [239, 132, 64], [118, 182, 74], [181, 126, 214], [219, 169, 42], [45, 183, 160], [224, 102, 143], [140, 155, 224]];
  const words = {
    fr: {
      scales: ['Fine', 'Intermédiaire', 'Globale'], region: 'Région', whole: 'Image entière',
      count: n => `${n} région${n > 1 ? 's' : ''} à cette échelle.`,
      hint: 'Sélectionnez une région pour la retrouver dans la hiérarchie.',
      selected: (name, share) => `${name} · ${share} % de l’image.`,
      error: 'La figure n’a pas pu être chargée. Rechargez la page pour réessayer.',
      image: name => `${name} : cliquez pour explorer les régions de la segmentation.`,
    },
    en: {
      scales: ['Fine', 'Intermediate', 'Global'], region: 'Region', whole: 'Whole image',
      count: n => `${n} region${n > 1 ? 's' : ''} at this scale.`,
      hint: 'Select a region to find it in the hierarchy.',
      selected: (name, share) => `${name} · ${share}% of the image.`,
      error: 'The figure could not be loaded. Reload the page to try again.',
      image: name => `${name}: click to explore the segmentation regions.`,
    },
  };
  const svgNS = 'http://www.w3.org/2000/svg';
  function svg(tag, attributes = {}, content) {
    const element = document.createElementNS(svgNS, tag);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    if (content !== undefined) element.textContent = content;
    return element;
  }
  function loadImage(url) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error(`Unable to load ${url}`));
      image.src = url;
    });
  }

  async function initialise(root) {
    if (root.dataset.initialised) return;
    root.dataset.initialised = 'true';
    const lang = root.dataset.lang === 'fr' ? 'fr' : 'en';
    const t = words[lang];
    const imageChoice = root.querySelector('.hierarchy-image-choice');
    const scaleInput = root.querySelector('.hierarchy-scale-input');
    const scaleOutput = root.querySelector('.hierarchy-scale-value');
    const photo = root.querySelector('.hierarchy-photo');
    const canvas = root.querySelector('.hierarchy-overlay');
    const context = canvas.getContext('2d');
    const tree = root.querySelector('.hierarchy-tree');
    const status = root.querySelector('.hierarchy-selection');
    const source = new URL(root.dataset.source, document.baseURI);
    const cache = new Map();
    const number = new Intl.NumberFormat(lang, { maximumFractionDigits: 2 });
    let sample, labels, cutMap, activeNodes, scale = 1, selected = null, anchor = null, request = 0;

    const colour = id => palette[(id - 1) % palette.length];
    const nodeName = id => id === sample.root ? t.whole : `${t.region} R${id}`;
    const node = id => sample.nodes[id - 1];
    const descendants = id => node(id).children.length ? node(id).children.flatMap(descendants) : [id];
    const share = id => number.format(100 * node(id).area / (sample.width * sample.height));

    function setBusy(busy) {
      root.setAttribute('aria-busy', String(busy));
      imageChoice.disabled = busy;
      scaleInput.disabled = busy;
      canvas.style.pointerEvents = busy ? 'none' : '';
    }

    function drawOverlay() {
      const imageData = context.createImageData(sample.width, sample.height);
      const pixels = imageData.data;
      const width = sample.width;
      for (let i = 0; i < labels.length; i++) {
        const id = cutMap[labels[i]], offset = 4 * i;
        const boundary = (i % width > 0 && cutMap[labels[i - 1]] !== id)
          || (i >= width && cutMap[labels[i - width]] !== id);
        const rgb = colour(id);
        pixels[offset] = rgb[0]; pixels[offset + 1] = rgb[1]; pixels[offset + 2] = rgb[2];
        pixels[offset + 3] = boundary ? 255 : id === selected ? 180 : 42;
      }
      context.putImageData(imageData, 0, 0);
    }

    function drawTree() {
      if (!sample) return;
      const width = Math.max(240, tree.parentElement.clientWidth);
      const height = 255;
      const leafOrder = descendants(sample.root);
      const spacing = (width - 36) / leafOrder.length;
      const radius = Math.min(9, spacing * .34);
      const positions = new Map();
      leafOrder.forEach((id, i) => positions.set(id, { x: 18 + spacing * (i + .5), y: 210 }));
      function place(id) {
        if (positions.has(id)) return positions.get(id);
        const children = node(id).children.map(place);
        const first = children[0], last = children[children.length - 1];
        const position = { x: (first.x + last.x) / 2, y: id === sample.root ? 35 : 120 };
        positions.set(id, position);
        return position;
      }
      place(sample.root);
      tree.setAttribute('viewBox', `0 0 ${width} ${height}`);
      // Reuse nodes during resize/selection so keyboard focus is preserved.
      const focused = tree.contains(document.activeElement) ? document.activeElement.dataset.node : null;
      tree.replaceChildren();
      const cutY = [165, 75, 3][scale];
      tree.append(svg('line', { x1: 6, x2: width - 6, y1: cutY, y2: cutY, class: 'hierarchy-cut' }));
      const branch = new Set();
      for (let id = selected; id; id = node(id).parent) branch.add(id);
      sample.nodes.forEach(n => {
        const p = positions.get(n.id);
        n.children.forEach(child => {
          const c = positions.get(child);
          tree.append(svg('path', { d: `M${p.x},${p.y}L${c.x},${c.y}`, class: `hierarchy-edge${branch.has(child) ? ' is-selected' : ''}` }));
        });
      });
      sample.nodes.forEach(n => {
        const p = positions.get(n.id);
        const isCut = activeNodes.has(n.id), isSelected = selected === n.id;
        const group = svg('g', {
          class: `hierarchy-node${isCut ? ' is-cut' : ''}${isSelected ? ' is-selected' : ''}`,
          transform: `translate(${p.x},${p.y})`, role: 'button', tabindex: '0',
          'data-node': n.id, 'aria-label': `${nodeName(n.id)}, ${share(n.id)} %`,
          'aria-pressed': String(isSelected), style: `--region-color:rgb(${colour(n.id).join(',')})`,
        });
        group.append(svg('title', {}, `${nodeName(n.id)} · ${share(n.id)} %`));
        group.append(svg('circle', { r: Math.min(18, spacing * .47), class: 'hierarchy-hit' }));
        group.append(svg('circle', { r: radius }));
        if (isSelected) group.append(svg('circle', { r: radius + 5, class: 'hierarchy-selection-ring' }));
        if (spacing >= 23 || isSelected || n.children.length) {
          group.append(svg('text', { y: n.children.length ? -17 : 25 }, n.id === sample.root ? t.whole : `R${n.id}`));
        }
        function choose() {
          anchor = n.anchor;
          selected = n.id;
          scale = n.level;
          scaleInput.value = scale;
          updateCut();
        }
        group.addEventListener('click', choose);
        group.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(); }
        });
        tree.append(group);
      });
      if (focused) {
        const replacement = tree.querySelector(`[data-node="${focused}"]`);
        if (replacement) replacement.focus({ preventScroll: true });
      }
    }

    function updateSelection() {
      status.textContent = `${t.count(activeNodes.size)} ${selected === null ? t.hint : t.selected(nodeName(selected), share(selected))}`;
      drawOverlay();
      drawTree();
    }

    function updateCut() {
      activeNodes = new Set(sample.cuts[scale]);
      cutMap = new Uint16Array(sample.cuts[0].length + 1);
      activeNodes.forEach(id => descendants(id).forEach(leaf => { cutMap[leaf] = id; }));
      if (anchor !== null) selected = cutMap[labels[anchor]];
      scaleOutput.textContent = t.scales[scale];
      scaleInput.setAttribute('aria-valuetext', `${t.scales[scale]}, ${t.count(activeNodes.size)}`);
      updateSelection();
    }

    async function loadSample(next) {
      const currentRequest = ++request;
      setBusy(true);
      try {
        if (!cache.has(next.id)) {
          cache.set(next.id, Promise.all([loadImage(new URL(next.image, source)), loadImage(new URL(next.labels, source))]));
        }
        const [image, mask] = await cache.get(next.id);
        if (currentRequest !== request) return;
        if (mask.naturalWidth !== next.width || mask.naturalHeight !== next.height) throw new Error('Invalid label map size');
        const decoder = document.createElement('canvas');
        decoder.width = next.width; decoder.height = next.height;
        const dc = decoder.getContext('2d', { willReadFrequently: true });
        dc.drawImage(mask, 0, 0);
        const rgba = dc.getImageData(0, 0, next.width, next.height).data;
        labels = new Uint8Array(next.width * next.height);
        for (let i = 0; i < labels.length; i++) labels[i] = rgba[4 * i];
        if (labels.some(id => id < 1 || id > next.cuts[0].length)) throw new Error('Invalid leaf label');
        sample = next; selected = null; anchor = null;
        photo.src = image.src;
        photo.width = next.width; photo.height = next.height;
        photo.alt = t.image(next.names[lang]);
        canvas.width = next.width; canvas.height = next.height;
        updateCut();
        setBusy(false);
      } catch (error) {
        if (currentRequest !== request) return;
        cache.delete(next.id);
        status.textContent = t.error;
        status.setAttribute('role', 'alert');
        console.error('Hierarchy figure:', error);
      }
    }

    try {
      const response = await fetch(source);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const manifest = await response.json();
      imageChoice.replaceChildren();
      manifest.samples.forEach(s => imageChoice.add(new Option(`${s.names[lang]} · ${s.id}`, s.id)));
      imageChoice.value = manifest.default;
      imageChoice.addEventListener('change', () => loadSample(manifest.samples.find(s => s.id === imageChoice.value)));
      scaleInput.addEventListener('input', () => { scale = Number(scaleInput.value); updateCut(); });
      canvas.addEventListener('click', event => {
        if (!sample || root.getAttribute('aria-busy') === 'true') return;
        const rect = canvas.getBoundingClientRect();
        const x = Math.min(sample.width - 1, Math.max(0, Math.floor((event.clientX - rect.left) * sample.width / rect.width)));
        const y = Math.min(sample.height - 1, Math.max(0, Math.floor((event.clientY - rect.top) * sample.height / rect.height)));
        anchor = y * sample.width + x;
        selected = cutMap[labels[anchor]];
        updateSelection();
      });
      new ResizeObserver(() => drawTree()).observe(tree.parentElement);
      await loadSample(manifest.samples.find(s => s.id === manifest.default));
    } catch (error) {
      status.textContent = t.error;
      status.setAttribute('role', 'alert');
      console.error('Hierarchy figure:', error);
    }
  }
  document.querySelectorAll('.hierarchy-demo').forEach(initialise);
})();
