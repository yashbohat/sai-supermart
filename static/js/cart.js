function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : '';
}

document.querySelectorAll('.cart-qty').forEach((input) => {
  input.addEventListener('change', async () => {
    const response = await fetch(input.dataset.updateUrl, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
      body: JSON.stringify({quantity: input.value})
    });
    if (!response.ok) return;
    const data = await response.json();
    const row = input.closest('[data-cart-item]');
    if (Number(input.value) === 0 && row) row.remove();
    if (row) row.querySelector('.item-total').textContent = `Rs. ${data.item_total}`;
    document.getElementById('cart-subtotal').textContent = data.subtotal;
    document.getElementById('cart-discount').textContent = data.discount;
    document.getElementById('cart-total').textContent = data.total;
  });
});

const menuToggle = document.querySelector('[data-menu-toggle]');
const mobileMenu = document.getElementById('mobile-menu');

if (menuToggle && mobileMenu) {
  menuToggle.addEventListener('click', () => {
    const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', String(!isOpen));
    mobileMenu.classList.toggle('max-h-0', isOpen);
    mobileMenu.classList.toggle('opacity-0', isOpen);
    mobileMenu.classList.toggle('max-h-[520px]', !isOpen);
    mobileMenu.classList.toggle('opacity-100', !isOpen);
    menuToggle.querySelector('.menu-open').classList.toggle('hidden', !isOpen);
    menuToggle.querySelector('.menu-close').classList.toggle('hidden', isOpen);
  });
}

const confettiCanvas = document.querySelector('[data-confetti]');
if (confettiCanvas) {
  const ctx = confettiCanvas.getContext('2d');
  const pieces = Array.from({length: 90}, () => ({
    x: Math.random() * window.innerWidth,
    y: -20 - Math.random() * 240,
    size: 5 + Math.random() * 8,
    speed: 2 + Math.random() * 4,
    drift: -1.5 + Math.random() * 3,
    color: ['#22C55E', '#16A34A', '#FEF9C3', '#F59E0B'][Math.floor(Math.random() * 4)],
    rotation: Math.random() * Math.PI
  }));
  let frame = 0;
  function resizeConfetti() {
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
  }
  function drawConfetti() {
    ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    pieces.forEach((piece) => {
      piece.y += piece.speed;
      piece.x += piece.drift;
      piece.rotation += 0.08;
      ctx.save();
      ctx.translate(piece.x, piece.y);
      ctx.rotate(piece.rotation);
      ctx.fillStyle = piece.color;
      ctx.fillRect(-piece.size / 2, -piece.size / 2, piece.size, piece.size * 0.6);
      ctx.restore();
    });
    frame += 1;
    if (frame < 170) requestAnimationFrame(drawConfetti);
  }
  resizeConfetti();
  window.addEventListener('resize', resizeConfetti);
  requestAnimationFrame(drawConfetti);
}
