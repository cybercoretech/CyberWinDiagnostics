// Themes: the universal Cybercore chooser (kit/chooser.js) owns the menu and palette.
const $ = (selector) => document.querySelector(selector);
const navToggle = $('#navToggle');
navToggle.addEventListener('click', () => {
  const expanded = navToggle.getAttribute('aria-expanded') === 'true';
  navToggle.setAttribute('aria-expanded', String(!expanded));
  navToggle.setAttribute('aria-label', expanded ? 'Open navigation' : 'Close navigation');
  $('.main-nav').classList.toggle('open', !expanded);
});
$('.main-nav').addEventListener('click', (event) => {
  if (event.target.closest('a')) {
    $('.main-nav').classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open navigation');
  }
});

$('#copyInstall').addEventListener('click', async () => {
  const command = $('#installCommand');
  try {
    await navigator.clipboard.writeText(command.textContent.trim());
    $('#copyStatus').textContent = 'COMMAND COPIED';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(command);
    selection.removeAllRanges();
    selection.addRange(range);
    $('#copyStatus').textContent = 'SELECTED — PRESS CTRL/CMD+C';
  }
});

