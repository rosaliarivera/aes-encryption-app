document.addEventListener('DOMContentLoaded', () => {
  const encryptRadio = document.querySelector('input[name="operation"][value="encrypt"]');
  const decryptRadio = document.querySelector('input[name="operation"][value="decrypt"]');
  const encSection = document.getElementById('encrypt-section');
  const decSection = document.getElementById('decrypt-section');

  function toggle() {
    if (encryptRadio.checked) {
      encSection.style.display = '';
      decSection.style.display = 'none';
    } else {
      encSection.style.display = 'none';
      decSection.style.display = '';
    }
  }

  encryptRadio.addEventListener('change', toggle);
  decryptRadio.addEventListener('change', toggle);
  toggle();
});
