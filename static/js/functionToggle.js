function toggle() {
  const toggleButton = document.getElementById("toggle");
  const togglelinks = document.getElementById('links');
  toggleButton.classList.toggle("active");
  togglelinks.classList.toggle('active');
}