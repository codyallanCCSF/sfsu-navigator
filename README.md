# SFSU Navigator

A web-based campus navigation app for San Francisco State University. The goal is an
interactive campus map where students can find buildings, view floor plans, see campus
events, and ask natural-language questions ("where is the nearest printer?") answered by
Gemini.

## Current Status

Early prototype. The Flask backend and API shape are in place, and there is a working
clickable campus map, but data, routing, floor plans, and the AI assistant are still stubs.

| Area | State |
| --- | --- |
| Flask backend (`app.py`) | Done: serves the frontend and JSON data endpoints |
| Interactive image map (`static/index.html`) | Working: 98 clickable building hotspots over an embedded campus map image, searchable building directory, search-to-highlight, selection panel, hotspots stay aligned on resize |
| Leaflet / OpenStreetMap map (`static/map.js`) | Skeleton: placeholder bounds; currently conflicts with the image map (see Known Issues) |
| Floor plans (`static/floorplan.js`) | Stub: `openFloorplan(id)` only shows placeholder text |
| Places data (`data/places.json`) | One placeholder entry |
| Events data (`data/events.json`) | Empty |
| Routing graph (`data/building_graph.json`) | Empty (`nodes`/`edges`) |
| AI assistant (`POST /api/ask`) | Stub: echoes the question; Gemini not called yet |
| Tests / CI | None |

## Project Structure

```
app.py                  Flask app and API routes
requirements.txt        flask, gunicorn, python-dotenv, google-genai
Procfile                gunicorn entrypoint (uses $PORT, for Cloud Run / buildpacks)
.env.example            GEMINI_API_KEY and GEMINI_MODEL template
.gcloudignore           Excludes .env, .venv, docs/ from Google Cloud deploys
data/
  places.json           Buildings / points of interest
  events.json           Campus events
  building_graph.json   Walkway graph for routing
static/
  index.html            Main page (image-based interactive map)
  map.js                Leaflet map that loads markers from /api/places
  floorplan.js          Floor plan overlay hooks
  style.css             Base styles
docs/
  reference/            Reference material (not deployed)
```

## API

| Method | Route | Returns |
| --- | --- | --- |
| GET | `/` | `static/index.html` |
| GET | `/api/places` | Contents of `data/places.json` |
| GET | `/api/events` | Contents of `data/events.json` |
| GET | `/api/graph` | Contents of `data/building_graph.json` |
| POST | `/api/ask` | Body `{"question": "..."}` → `{"answer", "place_ids", "event_ids", "route"}` (currently a stub) |

A place entry looks like:

```json
{"id": "annex1", "name": "Annex I", "lat": 37.7228, "lng": -122.4830,
 "category": "building", "has_floorplan": false}
```

## Running Locally

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your Gemini API key
python app.py               # http://localhost:8080
```

## Deployment

The `Procfile` and `.gcloudignore` are set up for Google Cloud (e.g. Cloud Run with
buildpacks):

```bash
gcloud run deploy sfsu-navigator --source . --set-env-vars GEMINI_API_KEY=...,GEMINI_MODEL=...
```

Because the app has a Python backend, it can no longer be hosted on GitHub Pages.

## Known Issues

- **Two maps fight over `#map`.** `index.html` contains the image map (`<div id="map">`)
  and a second empty `<div id="map">` for Leaflet. Both the inline script and `map.js`
  declare a top-level `const map`, so `map.js` throws
  `SyntaxError: Identifier 'map' has already been declared` and the Leaflet layer never
  loads. `style.css` also forces `#map` to `100vh`.
- **Large inline page.** `index.html` is ~2 MB because the campus map PNG is embedded as
  base64 and the hotspot regions are inlined in the script.
- **Hotspot data is duplicated and rectangular.** The 98 regions are hard-coded inline
  with only a name, and several names repeat (e.g. Fine Arts ×5, Administration ×5). They
  are not linked to `places.json` IDs.
- **Placeholder data.** Leaflet bounds, the single place's coordinates, and the Gemini
  model name in `.env.example` should all be verified.
- `static/reference_material/` is an empty, untracked folder; reference files belong in
  `docs/reference/`.

## Next Steps

1. **Pick one map approach and consolidate.** Decide between the image-hotspot map and the
   Leaflet/OSM map (or use the campus image as a Leaflet `imageOverlay` to get both).
   Remove whichever one is not used and fix the `#map` / `const map` collision.
2. **Move the map image and regions out of the HTML.** Save the PNG as
   `static/img/campus-map.png` and move the hotspot regions into `data/` (or into
   `places.json`) so the page is small and the data has one source of truth.
3. **Build out `places.json`.** Real coordinates, unique IDs, building codes (e.g. `TH`,
   `HSS`), categories (dining, library, parking, restrooms, printers), and accessibility
   info. Link each map hotspot to a place ID instead of a free-text name.
4. **Implement `POST /api/ask` with Gemini.** Use `google-genai` with `GEMINI_MODEL`, pass
   places/events as context, and ask for structured JSON output matching the existing
   response shape. Add input length limits, error handling, and a timeout.
5. **Add a chat / ask box to the frontend** that calls `/api/ask` and highlights the
   returned `place_ids` on the map.
6. **Routing.** Populate `building_graph.json` with walkway nodes and edges (including
   accessible routes, elevators, ramps), implement shortest-path (Dijkstra/A*) on the
   server, and draw the route on the map.
7. **Floor plans.** Collect floor plan images for a few key buildings, set
   `has_floorplan`, and replace the `openFloorplan` stub with a real viewer (floor
   selector, close button, room search).
8. **Events.** Define an event schema (title, time, place ID, link) and source data,
   either manually or from the SFSU events calendar, then show upcoming events per building.
9. **Quality basics.** Add pytest tests for the API routes, a GitHub Actions workflow,
   pinned dependency versions, and caching of the JSON files instead of reading from disk
   on every request.
10. **Accessibility and mobile polish.** Keyboard navigation for hotspots, ARIA labels,
    color contrast checks, and touch-friendly map interaction.
