(function () {
  const openBtn = document.getElementById("open-map-btn");
  const closeBtn = document.getElementById("close-map-btn");
  const confirmBtn = document.getElementById("confirm-map-btn");
  const modal = document.getElementById("map-modal");
  const venueInput = document.getElementById("lecture_venue");
  const latInput = document.getElementById("lat");
  const lngInput = document.getElementById("lng");
  const selectedLabel = document.getElementById("selected-location");

  if (!openBtn) return;

  let map;
  let marker;
  let selected = null;

  function showModal() {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    if (!map) {
      map = L.map("map").setView([7.3056, 5.1357], 18);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 20,
      }).addTo(map);
      map.on("click", onMapClick);
      setTimeout(() => map.invalidateSize(), 200);
    } else {
      setTimeout(() => map.invalidateSize(), 200);
    }
  }

  function hideModal() {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }

  async function reverseGeocode(lat, lng) {
    const response = await fetch(`/api/reverse-geocode?lat=${lat}&lng=${lng}`);
    const data = await response.json();
    return data.display_name || "Unknown location";
  }

  async function onMapClick(e) {
    const { lat, lng } = e.latlng;
    selected = { lat, lng, name: await reverseGeocode(lat, lng) };
    if (marker) marker.remove();
    marker = L.marker([lat, lng]).addTo(map).bindPopup(selected.name).openPopup();
    selectedLabel.innerHTML = `<b>Selected:</b> ${selected.name}`;
    confirmBtn.disabled = false;
  }

  openBtn.addEventListener("click", showModal);
  closeBtn.addEventListener("click", hideModal);
  confirmBtn.addEventListener("click", () => {
    if (!selected) return;
    venueInput.value = selected.name;
    latInput.value = selected.lat;
    lngInput.value = selected.lng;
    hideModal();
  });
})();
