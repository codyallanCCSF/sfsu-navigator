// OWNER: map person. Bounds below are rough placeholders: adjust after viewing the map.
const bounds = L.latLngBounds([37.7195, -122.4880], [37.7290, -122.4745]);
const map = L.map("map", { maxBounds: bounds, minZoom: 16 }).setView([37.7241, -122.4799], 16);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

fetch("/api/places").then(r => r.json()).then(places => {
  places.forEach(p => {
    const m = L.marker([p.lat, p.lng]).addTo(map).bindPopup(p.name);
    // Integration point: buildings with a floor plan open it on click.
    if (p.has_floorplan) m.on("click", () => openFloorplan(p.id));
  });
});
