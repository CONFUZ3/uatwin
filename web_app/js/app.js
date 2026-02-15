/**
 * UA Campus Digital Twin — MapLibre GL JS Application
 * Renders Overture Maps 3D buildings, OSM trees, parking lots,
 * green spaces, water features, and roads on an interactive map
 * with an analytics dashboard powered by Chart.js.
 */

// ─── Campus center ───
const CAMPUS_CENTER = [-87.5385, 33.2084];
const INITIAL_ZOOM = 15.2;
const INITIAL_PITCH = 55;
const INITIAL_BEARING = -15;

const HEIGHT_SCALE = 1.8;
const MIN_DISPLAY_HEIGHT = 6;

// ─── State ───
let buildingsData = null;
let treesData = null;
let parkingData = null;
let greenData = null;
let waterData = null;
let roadsData = null;
let landuseData = null;
let is3D = true;

// ─── Initialise map ───
const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        name: 'Dark',
        sources: {
            'carto-dark': {
                type: 'raster',
                tiles: [
                    'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
                    'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
                    'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'
                ],
                tileSize: 256,
                attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            }
        },
        layers: [{
            id: 'base-tiles',
            type: 'raster',
            source: 'carto-dark',
            minzoom: 0,
            maxzoom: 20
        }],
        glyphs: 'https://fonts.openmaptiles.org/{fontstack}/{range}.pbf'
    },
    center: CAMPUS_CENTER,
    zoom: INITIAL_ZOOM,
    pitch: INITIAL_PITCH,
    bearing: INITIAL_BEARING,
    maxPitch: 75,
    antialias: true
});

map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
map.addControl(new maplibregl.ScaleControl({ maxWidth: 200 }), 'bottom-right');

// ─── Load all data when map ready ───
map.on('load', async () => {
    // Load layers in visual stacking order (bottom to top)
    await Promise.all([
        loadGeneralLanduse(),
        loadGreenSpaces(),
        loadParking(),
        loadWater(),
        loadRoads(),
        loadBuildings(),
        loadTrees()
    ]);
    document.getElementById('loading').classList.add('hidden');
    buildCharts();
});

// ═══════════════════════════════════════════
// General Landuse (Base Layer)
// ═══════════════════════════════════════════

async function loadGeneralLanduse() {
    try {
        const res = await fetch('data/ua_landuse.geojson');
        if (!res.ok) throw new Error(`${res.status}`);
        landuseData = await res.json();

        map.addSource('landuse', { type: 'geojson', data: landuseData });

        map.addLayer({
            id: 'landuse-fill',
            type: 'fill',
            source: 'landuse',
            paint: {
                'fill-color': [
                    'match', ['get', 'landuse'],
                    'education', '#1e2235',
                    'residential', '#1c1f33',
                    'commercial', '#1c1f33',
                    'retail', '#1c1f33',
                    '#1a1d2e' // default
                ],
                'fill-opacity': 0.6
            }
        });

        map.addLayer({
            id: 'landuse-outline',
            type: 'line',
            source: 'landuse',
            paint: {
                'line-color': '#2a3a6b',
                'line-width': 1,
                'line-opacity': 0.2
            }
        });

        // Hover
        setupLayerHover('landuse-fill', f => {
            const name = f.properties.name || f.properties.landuse || 'Land Use';
            return name;
        });
    } catch (e) {
        console.warn('Landuse not loaded:', e.message);
    }
}

// ═══════════════════════════════════════════
// Green Spaces
// ═══════════════════════════════════════════

async function loadGreenSpaces() {
    try {
        const res = await fetch('data/ua_greenspaces.geojson');
        if (!res.ok) throw new Error(`${res.status}`);
        greenData = await res.json();
        setStat('greenCount', greenData.features.length);

        map.addSource('greenspaces', { type: 'geojson', data: greenData });

        map.addLayer({
            id: 'greenspaces-fill',
            type: 'fill',
            source: 'greenspaces',
            paint: {
                'fill-color': '#22c55e',
                'fill-opacity': 0.18
            }
        });

        map.addLayer({
            id: 'greenspaces-outline',
            type: 'line',
            source: 'greenspaces',
            paint: {
                'line-color': '#4ade80',
                'line-width': 1,
                'line-opacity': 0.5
            }
        });

        setupLayerHover('greenspaces-fill', f => {
            const name = f.properties.name || f.properties.leisure || f.properties.landuse || 'Green Space';
            return name;
        });
    } catch (e) {
        console.warn('Green spaces not loaded:', e.message);
        setStat('greenCount', '0');
    }
}

// ═══════════════════════════════════════════
// Parking Lots
// ═══════════════════════════════════════════

async function loadParking() {
    try {
        const res = await fetch('data/ua_parking.geojson');
        if (!res.ok) throw new Error(`${res.status}`);
        parkingData = await res.json();
        setStat('parkingCount', parkingData.features.length);

        map.addSource('parking', { type: 'geojson', data: parkingData });

        map.addLayer({
            id: 'parking-fill',
            type: 'fill',
            source: 'parking',
            paint: {
                'fill-color': '#f59e0b',
                'fill-opacity': 0.22
            }
        });

        map.addLayer({
            id: 'parking-outline',
            type: 'line',
            source: 'parking',
            paint: {
                'line-color': '#fbbf24',
                'line-width': 1,
                'line-opacity': 0.5
            }
        });

        setupLayerHover('parking-fill', f => {
            let label = f.properties.name || 'Parking Lot';
            if (f.properties.capacity) label += ` (${f.properties.capacity} spaces)`;
            return label;
        });
    } catch (e) {
        console.warn('Parking not loaded:', e.message);
        setStat('parkingCount', '0');
    }
}

// ═══════════════════════════════════════════
// Water Features
// ═══════════════════════════════════════════

async function loadWater() {
    try {
        const res = await fetch('data/ua_water.geojson');
        if (!res.ok) throw new Error(`${res.status}`);
        waterData = await res.json();
        setStat('waterCount', waterData.features.length);

        map.addSource('water', { type: 'geojson', data: waterData });

        // Polygon fills (lakes/ponds)
        map.addLayer({
            id: 'water-fill',
            type: 'fill',
            source: 'water',
            filter: ['any',
                ['==', ['geometry-type'], 'Polygon'],
                ['==', ['geometry-type'], 'MultiPolygon']
            ],
            paint: {
                'fill-color': '#0ea5e9',
                'fill-opacity': 0.3
            }
        });

        // Line features (streams/rivers)
        map.addLayer({
            id: 'water-line',
            type: 'line',
            source: 'water',
            filter: ['any',
                ['==', ['geometry-type'], 'LineString'],
                ['==', ['geometry-type'], 'MultiLineString']
            ],
            paint: {
                'line-color': '#38bdf8',
                'line-width': 2.5,
                'line-opacity': 0.6
            }
        });

        map.addLayer({
            id: 'water-outline',
            type: 'line',
            source: 'water',
            filter: ['any',
                ['==', ['geometry-type'], 'Polygon'],
                ['==', ['geometry-type'], 'MultiPolygon']
            ],
            paint: {
                'line-color': '#38bdf8',
                'line-width': 1.2,
                'line-opacity': 0.5
            }
        });

        setupLayerHover('water-fill', f => f.properties.name || 'Water');
    } catch (e) {
        console.warn('Water not loaded:', e.message);
        setStat('waterCount', '0');
    }
}

// ═══════════════════════════════════════════
// Roads & Paths
// ═══════════════════════════════════════════

async function loadRoads() {
    try {
        const res = await fetch('data/ua_roads.geojson');
        if (!res.ok) throw new Error(`${res.status}`);
        roadsData = await res.json();
        setStat('roadCount', roadsData.features.length);

        map.addSource('roads', { type: 'geojson', data: roadsData });

        // Major roads
        map.addLayer({
            id: 'roads-major',
            type: 'line',
            source: 'roads',
            filter: ['==', ['get', 'road_class'], 'major'],
            paint: {
                'line-color': '#cbd5e1',
                'line-width': ['interpolate', ['linear'], ['zoom'], 13, 1, 16, 3, 19, 6],
                'line-opacity': 0.5
            }
        });

        // Residential
        map.addLayer({
            id: 'roads-residential',
            type: 'line',
            source: 'roads',
            filter: ['==', ['get', 'road_class'], 'residential'],
            paint: {
                'line-color': '#94a3b8',
                'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.5, 16, 1.8, 19, 3.5],
                'line-opacity': 0.4
            }
        });

        // Service roads
        map.addLayer({
            id: 'roads-service',
            type: 'line',
            source: 'roads',
            filter: ['==', ['get', 'road_class'], 'service'],
            paint: {
                'line-color': '#64748b',
                'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.3, 16, 1, 19, 2],
                'line-opacity': 0.35
            }
        });

        // Pedestrian paths (dashed)
        map.addLayer({
            id: 'roads-pedestrian',
            type: 'line',
            source: 'roads',
            filter: ['==', ['get', 'road_class'], 'pedestrian'],
            paint: {
                'line-color': '#a78bfa',
                'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.3, 16, 1, 19, 2],
                'line-opacity': 0.35,
                'line-dasharray': [2, 2]
            }
        });
    } catch (e) {
        console.warn('Roads not loaded:', e.message);
        setStat('roadCount', '0');
    }
}

// ═══════════════════════════════════════════
// Buildings
// ═══════════════════════════════════════════

const buildingColorStops = [
    'interpolate', ['linear'],
    ['get', '_realHeight'],
    3, '#2a3a6b',
    8, '#3d5a9e',
    15, '#5b82cc',
    30, '#7eaaee',
    60, '#b4d4ff',
    100, '#e0edff'
];

async function loadBuildings() {
    try {
        const res = await fetch('data/ua_buildings.geojson');
        if (!res.ok) throw new Error(`Buildings file not found (${res.status})`);
        buildingsData = await res.json();

        // Normalise properties
        buildingsData.features.forEach((f, i) => {
            f.id = i;
            let h = parseFloat(f.properties.height);
            if (isNaN(h) || h <= 0) h = 8;
            f.properties._displayHeight = Math.max(h * HEIGHT_SCALE, MIN_DISPLAY_HEIGHT);
            f.properties._realHeight = h;
            f.properties._name = f.properties.display_name || '';
            f.properties._label = f.properties.display_name || '';
        });

        setStat('buildingCount', buildingsData.features.length);

        map.addSource('buildings', { type: 'geojson', data: buildingsData });

        // 3D extruded buildings
        map.addLayer({
            id: 'buildings-3d',
            type: 'fill-extrusion',
            source: 'buildings',
            paint: {
                'fill-extrusion-color': buildingColorStops,
                'fill-extrusion-height': ['get', '_displayHeight'],
                'fill-extrusion-base': 0,
                'fill-extrusion-opacity': 0.92
            }
        });

        // Top-edge outline
        map.addLayer({
            id: 'buildings-outline',
            type: 'line',
            source: 'buildings',
            paint: {
                'line-color': '#6b8fd4',
                'line-width': ['interpolate', ['linear'], ['zoom'], 14, 0.3, 17, 0.8],
                'line-opacity': 0.5
            }
        });

        // Labels
        map.addLayer({
            id: 'buildings-labels',
            type: 'symbol',
            source: 'buildings',
            filter: ['!=', ['get', '_label'], ''],
            layout: {
                'text-field': ['get', '_label'],
                'text-size': ['interpolate', ['linear'], ['zoom'], 14, 9, 16, 11, 18, 14],
                'text-anchor': 'top',
                'text-offset': [0, 0.8],
                'text-allow-overlap': false,
                'text-optional': true,
                'text-font': ['Open Sans Regular'],
                'text-max-width': 12,
                'symbol-sort-key': ['*', -1, ['get', '_realHeight']]
            },
            paint: {
                'text-color': '#d4ddf0',
                'text-halo-color': 'rgba(10, 12, 20, 0.9)',
                'text-halo-width': 2
            }
        });

        setupBuildingInteractions();
    } catch (err) {
        console.error('Error loading buildings:', err);
        setStat('buildingCount', 'Error');
    }
}

function setupBuildingInteractions() {
    let selectedId = null;

    // Click → show info panel and highlight
    map.on('click', 'buildings-3d', (e) => {
        if (!e.features || !e.features.length) return;
        const f = e.features[0];
        selectedId = f.id;
        showFeatureInfo(f.properties, 'building');

        map.setPaintProperty('buildings-3d', 'fill-extrusion-color', [
            'case',
            ['==', ['id'], f.id],
            '#fbbf24',
            buildingColorStops
        ]);
    });

    // Click away → deselect
    map.on('click', (e) => {
        const layers = ['buildings-3d', 'parking-fill', 'greenspaces-fill', 'water-fill', 'landuse-fill']
            .filter(id => map.getLayer(id));
        const features = map.queryRenderedFeatures(e.point, { layers });
        if (features.length === 0 && selectedId !== null) {
            selectedId = null;
            map.setPaintProperty('buildings-3d', 'fill-extrusion-color', buildingColorStops);
            document.getElementById('infoPanel').style.display = 'none';
        }
    });

    // Cursor
    map.on('mouseenter', 'buildings-3d', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'buildings-3d', () => map.getCanvas().style.cursor = '');

    // Tooltip
    const tooltip = document.getElementById('tooltip');
    map.on('mousemove', 'buildings-3d', (e) => {
        if (!e.features.length) return;
        const name = e.features[0].properties._name;
        const h = e.features[0].properties._realHeight;
        if (name || h) {
            tooltip.textContent = name ? `${name}  (${parseFloat(h).toFixed(1)}m)` : `${parseFloat(h).toFixed(1)}m`;
            const sidebarW = 320;
            tooltip.style.left = (e.point.x + sidebarW + 14) + 'px';
            tooltip.style.top = (e.point.y - 12) + 'px';
            tooltip.classList.add('visible');
        }
    });
    map.on('mouseleave', 'buildings-3d', () => tooltip.classList.remove('visible'));
}

// ═══════════════════════════════════════════
// Trees
// ═══════════════════════════════════════════

async function loadTrees() {
    try {
        const res = await fetch('data/ua_trees.geojson');
        if (!res.ok) throw new Error(`${res.status}`);
        treesData = await res.json();
        setStat('treeCount', treesData.features.length);

        map.addSource('trees', { type: 'geojson', data: treesData });

        // Canopy glow
        map.addLayer({
            id: 'trees-canopy',
            type: 'circle',
            source: 'trees',
            paint: {
                'circle-radius': ['interpolate', ['exponential', 2], ['zoom'], 13, 2, 16, 7, 19, 18],
                'circle-color': '#22c55e',
                'circle-opacity': 0.35,
                'circle-blur': 0.7
            }
        });

        // Core dot
        map.addLayer({
            id: 'trees-core',
            type: 'circle',
            source: 'trees',
            paint: {
                'circle-radius': ['interpolate', ['exponential', 2], ['zoom'], 13, 1, 16, 2.5, 19, 5],
                'circle-color': '#16a34a',
                'circle-opacity': 0.55
            }
        });
    } catch (e) {
        console.warn('Trees not loaded:', e.message);
        setStat('treeCount', '0');
    }
}

// ═══════════════════════════════════════════
// Generic hover helper
// ═══════════════════════════════════════════

function setupLayerHover(layerId, labelFn) {
    const tooltip = document.getElementById('tooltip');

    map.on('mouseenter', layerId, () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', layerId, () => {
        map.getCanvas().style.cursor = '';
        tooltip.classList.remove('visible');
    });

    map.on('mousemove', layerId, (e) => {
        if (!e.features.length) return;
        const text = labelFn(e.features[0]);
        if (text) {
            tooltip.textContent = text;
            const sidebarW = 320;
            tooltip.style.left = (e.point.x + sidebarW + 14) + 'px';
            tooltip.style.top = (e.point.y - 12) + 'px';
            tooltip.classList.add('visible');
        }
    });

    // Click → show info panel
    map.on('click', layerId, (e) => {
        if (!e.features.length) return;
        const f = e.features[0];
        const type = f.properties.layer_type || layerId.split('-')[0];
        showFeatureInfo(f.properties, type);
    });
}

// ═══════════════════════════════════════════
// Feature Info Panel
// ═══════════════════════════════════════════

function showFeatureInfo(props, type) {
    const panel = document.getElementById('infoPanel');
    const info = document.getElementById('buildingInfo');
    panel.style.display = 'block';

    let rows = [];

    if (type === 'building') {
        rows = [
            ['Name', props._name || '—'],
            ['Height', props._realHeight ? `${parseFloat(props._realHeight).toFixed(1)} m` : '—'],
            ['Class', props['class'] || '—'],
            ['Subtype', props.subtype || '—']
        ];
    } else if (type === 'parking') {
        rows = [
            ['Type', 'Parking Lot'],
            ['Name', props.name || '—'],
            ['Surface', props.surface || '—'],
            ['Capacity', props.capacity || '—'],
            ['Access', props.access || '—'],
            ['Fee', props.fee || '—']
        ];
    } else if (type === 'greenspace' || type === 'greenspaces') {
        rows = [
            ['Type', 'Green Space'],
            ['Name', props.name || '—'],
            ['Category', props.leisure || props.landuse || props.natural || '—'],
            ['Sport', props.sport || '—']
        ];
    } else if (type === 'water') {
        rows = [
            ['Type', 'Water Feature'],
            ['Name', props.name || '—'],
            ['Category', props.natural || props.waterway || props.water || '—']
        ];
    } else if (type === 'landuse') {
        rows = [
            ['Type', 'Land Use Area'],
            ['Name', props.name || '—'],
            ['Category', props.landuse || props.amenity || '—']
        ];
    } else {
        rows = Object.entries(props)
            .filter(([k]) => !k.startsWith('_'))
            .slice(0, 8)
            .map(([k, v]) => [k, v || '—']);
    }

    // Remove empty rows
    rows = rows.filter(([, v]) => v !== '—' || true);

    info.innerHTML = rows.map(([label, value]) => `
        <div class="info-row">
            <span class="info-label">${label}</span>
            <span class="info-value">${value}</span>
        </div>
    `).join('');
}

// ═══════════════════════════════════════════
// Search (searches buildings + parking + green + landuse)
// ═══════════════════════════════════════════

document.getElementById('searchInput').addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    const box = document.getElementById('searchResults');
    if (!q) { box.innerHTML = ''; return; }

    const hits = [];

    // Buildings
    if (buildingsData) {
        buildingsData.features
            .filter(f => (f.properties._name || '').toLowerCase().includes(q))
            .slice(0, 6)
            .forEach(f => hits.push({
                name: f.properties._name || 'Unnamed Building',
                tag: `${parseFloat(f.properties._realHeight).toFixed(0)}m`,
                type: 'building',
                geom: f.geometry,
                color: '#5b82cc'
            }));
    }

    // Parking
    if (parkingData) {
        parkingData.features
            .filter(f => (f.properties.name || '').toLowerCase().includes(q))
            .slice(0, 4)
            .forEach(f => hits.push({
                name: f.properties.name || 'Parking Lot',
                tag: f.properties.capacity ? `${f.properties.capacity} spaces` : '',
                type: 'parking',
                geom: f.geometry,
                color: '#f59e0b'
            }));
    }

    // Green spaces
    if (greenData) {
        greenData.features
            .filter(f => (f.properties.name || '').toLowerCase().includes(q))
            .slice(0, 4)
            .forEach(f => hits.push({
                name: f.properties.name || 'Green Space',
                tag: '',
                type: 'green',
                geom: f.geometry,
                color: '#4ade80'
            }));
    }

    box.innerHTML = hits.slice(0, 10).map((h, i) => `
        <div class="search-item" data-idx="${i}">
            <i class="dot" style="background:${h.color}"></i>
            ${h.name}
            <span class="search-height">${h.tag}</span>
        </div>
    `).join('');

    box.querySelectorAll('.search-item').forEach(el => {
        el.addEventListener('click', () => {
            const idx = parseInt(el.dataset.idx);
            const hit = hits[idx];
            if (hit) {
                const c = getCentroid(hit.geom);
                map.flyTo({ center: c, zoom: 17.5, pitch: 60, duration: 1400 });
            }
            box.innerHTML = '';
            e.target.value = '';
        });
    });
});

function getCentroid(geom) {
    if (geom.type === 'Point') return geom.coordinates;
    let ring = geom.coordinates;
    if (geom.type === 'MultiPolygon') ring = ring[0];
    if (Array.isArray(ring[0]) && Array.isArray(ring[0][0])) ring = ring[0];
    let sx = 0, sy = 0;
    ring.forEach(c => { sx += c[0]; sy += c[1]; });
    return [sx / ring.length, sy / ring.length];
}

// ═══════════════════════════════════════════
// Charts (Chart.js)
// ═══════════════════════════════════════════

function buildCharts() {
    buildHeightChart();
    buildLanduseChart();
}

function buildHeightChart() {
    if (!buildingsData) return;
    const heights = buildingsData.features.map(f => parseFloat(f.properties._realHeight) || 8);

    // Bucket into ranges
    const ranges = ['0-5m', '5-10m', '10-15m', '15-25m', '25-50m', '50m+'];
    const buckets = [0, 0, 0, 0, 0, 0];
    heights.forEach(h => {
        if (h < 5) buckets[0]++;
        else if (h < 10) buckets[1]++;
        else if (h < 15) buckets[2]++;
        else if (h < 25) buckets[3]++;
        else if (h < 50) buckets[4]++;
        else buckets[5]++;
    });

    const ctx = document.getElementById('heightChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ranges,
            datasets: [{
                label: 'Buildings',
                data: buckets,
                backgroundColor: [
                    'rgba(42, 58, 107, 0.8)',
                    'rgba(61, 90, 158, 0.8)',
                    'rgba(91, 130, 204, 0.8)',
                    'rgba(126, 170, 238, 0.8)',
                    'rgba(180, 212, 255, 0.8)',
                    'rgba(224, 237, 255, 0.8)'
                ],
                borderColor: 'rgba(108, 140, 255, 0.3)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(20, 22, 32, 0.95)',
                    titleColor: '#e8eaf0',
                    bodyColor: '#8b8fa8',
                    borderColor: '#1e2235',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: { color: '#5a5e76', font: { size: 10 } },
                    grid: { color: 'rgba(30, 34, 53, 0.5)' }
                },
                y: {
                    ticks: { color: '#5a5e76', font: { size: 10 } },
                    grid: { color: 'rgba(30, 34, 53, 0.5)' }
                }
            }
        }
    });
}

function buildLanduseChart() {
    const counts = {
        'Buildings': buildingsData ? buildingsData.features.length : 0,
        'Parking': parkingData ? parkingData.features.length : 0,
        'Green Space': greenData ? greenData.features.length : 0,
        'Water': waterData ? waterData.features.length : 0,
        'Trees': treesData ? treesData.features.length : 0,
        'Land Use': landuseData ? landuseData.features.length : 0
    };

    // Remove zero entries
    const labels = Object.keys(counts).filter(k => counts[k] > 0);
    const data = labels.map(k => counts[k]);
    const colors = {
        'Buildings': '#5b82cc',
        'Parking': '#f59e0b',
        'Green Space': '#4ade80',
        'Water': '#38bdf8',
        'Trees': '#22c55e',
        'Land Use': '#2a3a6b'
    };

    const ctx = document.getElementById('landuseChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: labels.map(l => colors[l] || '#6c8cff'),
                borderColor: 'rgba(12, 14, 20, 0.8)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#8b8fa8',
                        padding: 10,
                        font: { size: 11 },
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(20, 22, 32, 0.95)',
                    titleColor: '#e8eaf0',
                    bodyColor: '#8b8fa8',
                    borderColor: '#1e2235',
                    borderWidth: 1
                }
            }
        }
    });
}

// ═══════════════════════════════════════════
// UI Controls
// ═══════════════════════════════════════════

function setStat(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = typeof value === 'number' ? value.toLocaleString() : value;
}

// Layer toggles
const layerToggles = {
    'toggleBuildings': ['buildings-3d', 'buildings-outline', 'buildings-labels'],
    'toggleTrees': ['trees-canopy', 'trees-core'],
    'toggleGreen': ['greenspaces-fill', 'greenspaces-outline'],
    'toggleParking': ['parking-fill', 'parking-outline'],
    'toggleWater': ['water-fill', 'water-line', 'water-outline'],
    'toggleRoads': ['roads-major', 'roads-residential', 'roads-service', 'roads-pedestrian'],
    'toggleLanduse': ['landuse-fill', 'landuse-outline'],
    'toggleLabels': ['buildings-labels']
};

Object.entries(layerToggles).forEach(([toggleId, layerIds]) => {
    const el = document.getElementById(toggleId);
    if (!el) return;
    el.addEventListener('change', (e) => {
        const v = e.target.checked ? 'visible' : 'none';
        layerIds.forEach(id => {
            if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', v);
        });
    });
});

document.getElementById('resetViewBtn').addEventListener('click', () => {
    map.flyTo({
        center: CAMPUS_CENTER,
        zoom: INITIAL_ZOOM,
        pitch: INITIAL_PITCH,
        bearing: INITIAL_BEARING,
        duration: 1400
    });
});

document.getElementById('togglePitchBtn').addEventListener('click', () => {
    is3D = !is3D;
    map.easeTo({
        pitch: is3D ? INITIAL_PITCH : 0,
        bearing: is3D ? INITIAL_BEARING : 0,
        duration: 700
    });
});
