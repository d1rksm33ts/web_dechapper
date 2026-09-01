const header = document.querySelector('[data-header]');
const navToggle = document.querySelector('[data-nav-toggle]');
const navigation = document.querySelector('[data-navigation]');

const updateHeader = () => header?.classList.toggle('scrolled', window.scrollY > 30);
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

navToggle?.addEventListener('click', () => {
  const open = navToggle.getAttribute('aria-expanded') === 'true';
  navToggle.setAttribute('aria-expanded', String(!open));
  navigation.classList.toggle('open', !open);
});
navigation?.addEventListener('click', (event) => {
  if (event.target.matches('a')) {
    navigation.classList.remove('open');
    navToggle?.setAttribute('aria-expanded', 'false');
  }
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => entry.target.classList.toggle('is-visible', entry.isIntersecting));
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));

const dialog = document.querySelector('[data-lightbox]');
const dialogImage = dialog?.querySelector('img');
document.querySelectorAll('[data-image]').forEach((button) => button.addEventListener('click', () => {
  dialogImage.src = button.dataset.image;
  dialogImage.alt = button.querySelector('img').alt;
  dialog.showModal();
}));
dialog?.querySelector('[data-lightbox-close]').addEventListener('click', () => dialog.close());
dialog?.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });

window.dechapperRecaptcha = (token) => {
  const input = document.querySelector('[name="recaptcha_token"]');
  if (input) input.value = token;
};

const form = document.querySelector('[data-contact-form]');
form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  const status = form.querySelector('[data-form-status]');
  button.disabled = true;
  status.textContent = 'Uw aanvraag wordt verstuurd…';
  status.className = 'form-status';
  try {
    const response = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    const result = await response.json();
    status.textContent = result.message;
    status.classList.add(response.ok ? 'success' : 'error');
    if (response.ok) { form.reset(); if (window.grecaptcha) window.grecaptcha.reset(); }
  } catch (_) {
    status.textContent = 'Er ging iets mis. Probeer later opnieuw of mail ons rechtstreeks.';
    status.classList.add('error');
  } finally { button.disabled = false; }
});

