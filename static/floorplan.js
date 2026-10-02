// OWNER: floor plan pair. The map calls openFloorplan(buildingId) on click.
function openFloorplan(buildingId) {
  const el = document.getElementById("floorplan");
  el.hidden = false;
  el.textContent = "Floor plan for " + buildingId + " goes here.";
}
function closeFloorplan() {
  document.getElementById("floorplan").hidden = true;
}
