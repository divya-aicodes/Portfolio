const menuButton = document.querySelector('.menu-button');
const siteNav = document.querySelector('.site-nav');
const header = document.querySelector('[data-header]');
const progressBar = document.querySelector('#scroll-progress-bar');
const heroSection = document.querySelector('#top');

function closeMenu() {
  if (!menuButton || !siteNav) return;
  menuButton.setAttribute('aria-expanded', 'false');
  siteNav.classList.remove('is-open');
}

menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  siteNav?.classList.toggle('is-open', !isOpen);
});

siteNav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeMenu();
});

function updateScrollUI() {
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
  if (progressBar) progressBar.style.transform = `scaleX(${progress})`;
  header?.classList.toggle('is-scrolled', window.scrollY > 24);
  header?.classList.toggle('on-dark', Boolean(heroSection) && window.scrollY < heroSection.offsetHeight - 90);
}

window.addEventListener('scroll', updateScrollUI, { passive: true });
updateScrollUI();

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduceMotion && 'IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px' });
  document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));
} else {
  document.querySelectorAll('.reveal').forEach((element) => element.classList.add('is-visible'));
}

const sectionLinks = document.querySelectorAll('.site-nav a[href^="#"], .section-rail a[href^="#"]');
const pageSections = [...new Set([...sectionLinks]
  .map((link) => document.querySelector(link.getAttribute('href')))
  .filter(Boolean))];

if ('IntersectionObserver' in window) {
  const sectionObserver = new IntersectionObserver((entries) => {
    const visibleSection = entries
      .filter((entry) => entry.isIntersecting)
      .sort((first, second) => second.intersectionRatio - first.intersectionRatio)[0];
    if (!visibleSection) return;

    sectionLinks.forEach((link) => {
      const isActive = link.getAttribute('href') === `#${visibleSection.target.id}`;
      link.classList.toggle('is-active', isActive);
      if (isActive) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-32% 0px -52%', threshold: [0, 0.15, 0.4] });

  pageSections.forEach((section) => sectionObserver.observe(section));
}

const counters = document.querySelectorAll('[data-count]');

function setCounterValue(element, value) {
  const padding = Number(element.dataset.pad || 1);
  element.textContent = String(value).padStart(padding, '0');
}

function animateCounter(element) {
  const target = Number(element.dataset.count || 0);
  const startedAt = performance.now();
  const duration = 900;

  function tick(now) {
    const progress = Math.min((now - startedAt) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    setCounterValue(element, Math.round(target * eased));
    if (progress < 1) requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
}

if (!reduceMotion && 'IntersectionObserver' in window) {
  const counterObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      animateCounter(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.75 });
  counters.forEach((counter) => counterObserver.observe(counter));
} else {
  counters.forEach((counter) => setCounterValue(counter, Number(counter.dataset.count || 0)));
}

const focusRotator = document.querySelector('#focus-rotator');
const focusMessages = [
  'python · ai systems · product craft',
  'react · accessible interfaces · clarity',
  'apis · simulation · responsible ai',
];

if (focusRotator && !reduceMotion) {
  let focusIndex = 0;
  window.setInterval(() => {
    focusRotator.classList.add('is-changing');
    window.setTimeout(() => {
      focusIndex = (focusIndex + 1) % focusMessages.length;
      focusRotator.textContent = focusMessages[focusIndex];
      focusRotator.classList.remove('is-changing');
    }, 180);
  }, 2800);
}

function attachTilt(element, options) {
  element.addEventListener('pointermove', (event) => {
    const bounds = element.getBoundingClientRect();
    const horizontal = (event.clientX - bounds.left) / bounds.width - 0.5;
    const vertical = (event.clientY - bounds.top) / bounds.height - 0.5;
    element.style.setProperty(options.xProperty, `${(-vertical * options.strength).toFixed(2)}deg`);
    element.style.setProperty(options.yProperty, `${(horizontal * options.strength).toFixed(2)}deg`);
  });

  element.addEventListener('pointerleave', () => {
    element.style.setProperty(options.xProperty, '0deg');
    element.style.setProperty(options.yProperty, '0deg');
  });
}

if (!reduceMotion && window.matchMedia('(pointer: fine)').matches) {
  document.querySelectorAll('[data-tilt]').forEach((element) => attachTilt(element, {
    xProperty: '--tilt-x',
    yProperty: '--tilt-y',
    strength: 8,
  }));

  document.querySelectorAll('[data-tilt-card]').forEach((element) => attachTilt(element, {
    xProperty: '--card-tilt-x',
    yProperty: '--card-tilt-y',
    strength: 2.5,
  }));
}

document.querySelectorAll('[data-project-card]').forEach((card) => {
  card.addEventListener('pointermove', (event) => {
    const bounds = card.getBoundingClientRect();
    card.style.setProperty('--pointer-x', `${event.clientX - bounds.left}px`);
    card.style.setProperty('--pointer-y', `${event.clientY - bounds.top}px`);
  });
});

const hypercubeCanvas = document.querySelector('#hypercube-canvas');
const heroVisual = document.querySelector('.hero-visual');

if (hypercubeCanvas && heroVisual) {
  const context = hypercubeCanvas.getContext('2d');
  const vertices = Array.from({ length: 16 }, (_, index) => [
    index & 1 ? 1 : -1,
    index & 2 ? 1 : -1,
    index & 4 ? 1 : -1,
    index & 8 ? 1 : -1,
  ]);
  const edges = [];

  for (let vertex = 0; vertex < vertices.length; vertex += 1) {
    for (let dimension = 0; dimension < 4; dimension += 1) {
      const neighbor = vertex ^ (1 << dimension);
      if (vertex < neighbor) edges.push([vertex, neighbor, dimension]);
    }
  }

  const motion = { x: 0, y: 0, targetX: 0, targetY: 0 };
  let canvasWidth = 0;
  let canvasHeight = 0;
  let animationFrame = 0;
  let isVisible = true;

  function rotatePlane(point, firstAxis, secondAxis, angle) {
    const cosine = Math.cos(angle);
    const sine = Math.sin(angle);
    const first = point[firstAxis] * cosine - point[secondAxis] * sine;
    const second = point[firstAxis] * sine + point[secondAxis] * cosine;
    point[firstAxis] = first;
    point[secondAxis] = second;
  }

  function resizeHypercube() {
    const bounds = hypercubeCanvas.getBoundingClientRect();
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
    canvasWidth = Math.max(1, bounds.width);
    canvasHeight = Math.max(1, bounds.height);
    hypercubeCanvas.width = Math.round(canvasWidth * pixelRatio);
    hypercubeCanvas.height = Math.round(canvasHeight * pixelRatio);
    context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  }

  function projectVertex(source, elapsed) {
    const point = [...source];
    const scrollPhase = window.scrollY * 0.00055;

    rotatePlane(point, 0, 3, elapsed * 0.00034 + motion.x * 0.7 + scrollPhase);
    rotatePlane(point, 1, 3, elapsed * 0.00023 + motion.y * 0.65);
    rotatePlane(point, 2, 3, elapsed * 0.00017 + scrollPhase * 0.45);
    rotatePlane(point, 0, 1, elapsed * 0.00011);

    const fourDimensionalScale = 2.7 / (3.8 - point[3]);
    let x = point[0] * fourDimensionalScale;
    let y = point[1] * fourDimensionalScale;
    let z = point[2] * fourDimensionalScale;

    const yaw = 0.55 + motion.x * 0.45;
    const pitch = -0.28 + motion.y * 0.35;
    const yawX = x * Math.cos(yaw) - z * Math.sin(yaw);
    const yawZ = x * Math.sin(yaw) + z * Math.cos(yaw);
    x = yawX;
    z = yawZ;
    const pitchY = y * Math.cos(pitch) - z * Math.sin(pitch);
    const pitchZ = y * Math.sin(pitch) + z * Math.cos(pitch);
    y = pitchY;
    z = pitchZ;

    const perspective = 4.4 / (4.4 - z);
    const size = Math.min(canvasWidth, canvasHeight) * 0.3;
    return {
      x: canvasWidth * 0.5 + x * perspective * size,
      y: canvasHeight * 0.48 + y * perspective * size,
      depth: perspective,
    };
  }

  function drawHypercube(elapsed = 0) {
    if (!context || !canvasWidth || !canvasHeight) return;
    context.clearRect(0, 0, canvasWidth, canvasHeight);
    motion.x += (motion.targetX - motion.x) * 0.055;
    motion.y += (motion.targetY - motion.y) * 0.055;

    const projected = vertices.map((vertex) => projectVertex(vertex, elapsed));
    const styles = getComputedStyle(document.documentElement);
    const colors = [
      styles.getPropertyValue('--hero-lime').trim() || styles.getPropertyValue('--blue').trim(),
      styles.getPropertyValue('--hero-line').trim() || styles.getPropertyValue('--ink').trim(),
      styles.getPropertyValue('--white').trim(),
      styles.getPropertyValue('--orange').trim(),
    ];

    edges.forEach(([startIndex, endIndex, dimension]) => {
      const start = projected[startIndex];
      const end = projected[endIndex];
      context.beginPath();
      context.moveTo(start.x, start.y);
      context.lineTo(end.x, end.y);
      context.strokeStyle = colors[dimension];
      context.globalAlpha = 0.28 + Math.min(start.depth, end.depth) * 0.34;
      context.lineWidth = dimension === 3 ? 2 : 1.25;
      context.stroke();
    });

    projected.forEach((point, index) => {
      context.beginPath();
      context.arc(point.x, point.y, Math.max(1.5, point.depth * 2.2), 0, Math.PI * 2);
      context.fillStyle = index % 2 ? colors[0] : colors[2];
      context.globalAlpha = 0.8;
      context.fill();
    });

    context.globalAlpha = 1;
  }

  function animateHypercube(elapsed) {
    drawHypercube(elapsed);
    if (isVisible && !reduceMotion) animationFrame = requestAnimationFrame(animateHypercube);
  }

  heroVisual.addEventListener('pointermove', (event) => {
    const bounds = heroVisual.getBoundingClientRect();
    motion.targetX = ((event.clientX - bounds.left) / bounds.width - 0.5) * 2;
    motion.targetY = ((event.clientY - bounds.top) / bounds.height - 0.5) * 2;
  });

  heroVisual.addEventListener('pointerleave', () => {
    motion.targetX = 0;
    motion.targetY = 0;
  });

  const hypercubeObserver = new IntersectionObserver(([entry]) => {
    isVisible = entry.isIntersecting;
    cancelAnimationFrame(animationFrame);
    if (isVisible) animationFrame = requestAnimationFrame(animateHypercube);
  }, { rootMargin: '120px' });

  new ResizeObserver(() => {
    resizeHypercube();
    if (reduceMotion) drawHypercube(1200);
  }).observe(hypercubeCanvas);

  hypercubeObserver.observe(heroVisual);
}

const runPythonButton = document.querySelector('#run-python');
const terminalOutput = document.querySelector('#terminal-output');

runPythonButton?.addEventListener('click', async () => {
  runPythonButton.disabled = true;
  runPythonButton.firstChild.textContent = 'Running… ';
  if (terminalOutput) terminalOutput.innerHTML = '<p><b>$</b> GET /api/profile</p><p class="terminal-muted">Waiting for Flask…</p>';

  try {
    const response = await fetch('/api/profile', { headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('The endpoint returned an error.');
    const data = await response.json();
    if (terminalOutput) {
      terminalOutput.innerHTML = `
        <p><b>$</b> GET /api/profile <strong class="terminal-ok">200 OK</strong></p>
        <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
        <p class="terminal-muted"># Response generated live by ${escapeHtml(data.served_by)}.</p>`;
    }
  } catch (error) {
    if (terminalOutput) terminalOutput.innerHTML = `<p class="terminal-error">Could not reach Python: ${escapeHtml(error.message)}</p>`;
  } finally {
    runPythonButton.disabled = false;
    runPythonButton.firstChild.textContent = 'Run Python endpoint ';
  }
});

const contactForm = document.querySelector('#contact-form');
const formStatus = document.querySelector('#form-status');

function clearFormErrors() {
  document.querySelectorAll('.field-error').forEach((element) => { element.textContent = ''; });
  document.querySelectorAll('.form-field input, .form-field textarea').forEach((element) => element.removeAttribute('aria-invalid'));
}

contactForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearFormErrors();

  const submitButton = contactForm.querySelector('button[type="submit"]');
  const formData = new FormData(contactForm);
  const payload = Object.fromEntries(formData.entries());
  submitButton.disabled = true;
  formStatus.textContent = 'Sending your note…';
  formStatus.className = 'form-status';

  try {
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      Object.entries(data.fields || {}).forEach(([field, message]) => {
        const input = contactForm.elements[field];
        const error = document.querySelector(`[data-error-for="${field}"]`);
        if (input) input.setAttribute('aria-invalid', 'true');
        if (error) error.textContent = message;
      });
      throw new Error(data.error || 'Unable to send your message.');
    }

    contactForm.reset();
    if (data.csrf_token) contactForm.elements.csrf_token.value = data.csrf_token;
    formStatus.textContent = data.message;
    formStatus.className = 'form-status is-success';
  } catch (error) {
    formStatus.textContent = error.message;
    formStatus.className = 'form-status is-error';
  } finally {
    submitButton.disabled = false;
  }
});

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
  })[character]);
}
