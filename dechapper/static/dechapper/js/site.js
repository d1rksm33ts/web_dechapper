const header = document.querySelector('[data-header]');
const navigation = document.querySelector('[data-navigation]');
const navToggle = document.querySelector('[data-nav-toggle]');
const backToTop = document.querySelector('.back-to-top');

const updateScrollState = () => {
  const scrolled = window.scrollY > 80;
  header?.classList.toggle('header-scrolled', scrolled);
  backToTop?.classList.toggle('active', scrolled);
};
updateScrollState();
window.addEventListener('scroll', updateScrollState, { passive: true });

navToggle?.addEventListener('click', () => {
  const open = navigation.classList.toggle('navbar-mobile');
  navToggle.setAttribute('aria-expanded', String(open));
  navToggle.lastChild.textContent = open ? '×' : '☰';
});
navigation?.addEventListener('click', (event) => {
  if (!event.target.closest('a') || !navigation.classList.contains('navbar-mobile')) return;
  navigation.classList.remove('navbar-mobile');
  navToggle.setAttribute('aria-expanded', 'false');
  navToggle.lastChild.textContent = '☰';
});

const sections = [...document.querySelectorAll('main section[id], #hero')];
const navLinks = [...document.querySelectorAll('.navbar .scrollto')];
const sectionObserver = new IntersectionObserver((entries) => {
  const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  navLinks.forEach((link) => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
}, { rootMargin: '-25% 0px -60%', threshold: [0, .2, .5] });
sections.forEach((section) => sectionObserver.observe(section));

document.querySelectorAll('#portfolio-flters li').forEach((filter) => filter.addEventListener('click', () => {
  document.querySelectorAll('#portfolio-flters li').forEach((item) => item.classList.remove('filter-active'));
  filter.classList.add('filter-active');
  const selector = filter.dataset.filter;
  document.querySelectorAll('.portfolio-item').forEach((item) => {
    item.hidden = selector !== '*' && !item.matches(selector);
  });
}));

const dialog = document.querySelector('[data-lightbox]');
const dialogImage = dialog?.querySelector('img');
document.querySelectorAll('.portfolio-lightbox').forEach((link) => link.addEventListener('click', (event) => {
  event.preventDefault();
  dialogImage.src = link.href;
  dialogImage.alt = link.title || 'Realisatie van De Chapper';
  dialog.showModal();
}));
dialog?.querySelector('[data-lightbox-close]')?.addEventListener('click', () => dialog.close());
dialog?.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });

const form = document.querySelector('[data-contact-form]');
const clearFieldError = (field) => {
  field?.classList.remove('is-invalid');
  field?.removeAttribute('aria-invalid');
  const feedback = form?.querySelector(`[data-field-error="${field?.name}"]`);
  if (feedback) { feedback.textContent = ''; feedback.classList.remove('visible'); }
};
const showFieldError = (name, message) => {
  const field = form?.elements.namedItem(name);
  const feedback = form?.querySelector(`[data-field-error="${name}"]`);
  field?.classList.add('is-invalid');
  field?.setAttribute('aria-invalid', 'true');
  if (feedback) { feedback.textContent = message; feedback.classList.add('visible'); }
  return field;
};
form?.querySelectorAll('input, textarea').forEach((field) => {
  field.addEventListener('input', () => { field.setCustomValidity(''); clearFieldError(field); });
  field.addEventListener('invalid', () => {
    let message = field.validationMessage;
    if (field.validity.rangeUnderflow && field.dataset.minMessage) message = field.dataset.minMessage;
    if (field.validity.rangeOverflow && field.dataset.maxMessage) message = field.dataset.maxMessage;
    field.setCustomValidity(message);
    showFieldError(field.name, message);
  });
});
form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  const status = form.querySelector('[data-form-status]');
  form.querySelectorAll('input, textarea').forEach(clearFieldError);
  button.disabled = true;
  status.textContent = 'Uw aanvraag wordt verstuurd…';
  status.className = 'form-status';
  try {
    const response = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    const result = await response.json();
    let firstInvalidField = null;
    Object.entries(result.errors || {}).forEach(([name, errors]) => {
      const message = errors.map((error) => error.message).join(' ');
      firstInvalidField ||= showFieldError(name, message);
    });
    status.textContent = firstInvalidField ? 'Controleer de gemarkeerde velden.' : result.message;
    status.classList.add(response.ok ? 'success' : 'error');
    if (response.ok) { form.reset(); if (window.turnstile) window.turnstile.reset(); }
    else { firstInvalidField?.focus(); if (window.turnstile) window.turnstile.reset(); }
  } catch (_) {
    status.textContent = 'Er ging iets mis. Probeer later opnieuw of mail ons rechtstreeks.';
    status.classList.add('error');
  } finally { button.disabled = false; }
});
