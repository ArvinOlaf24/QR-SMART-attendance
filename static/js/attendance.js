function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3;
  const toRad = (deg) => (deg * Math.PI) / 180;
  const phi1 = toRad(lat1);
  const phi2 = toRad(lat2);
  const deltaPhi = toRad(lat2 - lat1);
  const deltaLambda = toRad(lon2 - lon1);
  const a =
    Math.sin(deltaPhi / 2) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function initAttendancePage({ lat, lng }) {
  const distanceDisplay = document.getElementById("distance-display");
  const submitBtn = document.getElementById("submit-btn");
  const rangeWarning = document.getElementById("range-warning");
  const form = document.getElementById("attendance-form");
  const userLatInput = document.getElementById("user_lat");
  const userLngInput = document.getElementById("user_lng");

  if (!navigator.geolocation) {
    distanceDisplay.textContent = "Geolocation not supported";
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const userLat = position.coords.latitude;
      const userLng = position.coords.longitude;
      const distance = calculateDistance(userLat, userLng, lat, lng);

      userLatInput.value = userLat;
      userLngInput.value = userLng;
      distanceDisplay.textContent = `${distance.toFixed(2)} meters`;

      if (distance <= 20) {
        submitBtn.classList.remove("hidden");
        rangeWarning.classList.add("hidden");
        form.classList.remove("hidden");
      } else {
        submitBtn.classList.add("hidden");
        rangeWarning.classList.remove("hidden");
      }
    },
    (error) => {
      distanceDisplay.textContent = `Error: ${error.message}`;
    }
  );
}
