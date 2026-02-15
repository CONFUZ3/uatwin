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
let scheduleData = null;
let mySchedule = [];
let is3D = true;
let isPlaying = false;
let playInterval = null;
let currentDayFilter = 'Mon';
let currentTimeMinutes = 600; // 10:00 AM

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

// ─── Right Sidebar Toggle ───
const rightSidebar = document.getElementById('sidebar-right');
const toggleBtn = document.getElementById('toggleRightSidebar');
toggleBtn.addEventListener('click', () => {
    rightSidebar.classList.toggle('collapsed');
    document.body.classList.toggle('right-open');
    // Let map resize after CSS transition
    setTimeout(() => map.resize(), 400);
});


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
        loadTrees(),
        loadSchedule()
    ]);
    document.getElementById('loading').classList.add('hidden');
    buildCharts();
    setupTimeControls();
    setupCourseScheduleUI();
});

async function loadSchedule() {
    try {
        const res = await fetch('data/ua_class_schedule.json');
        if (!res.ok) throw new Error(`${res.status}`);
        scheduleData = await res.json();
    } catch (e) {
        console.warn('Schedule data not loaded:', e.message);
    }
}

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
                // Initial color, will be overridden by occupancy
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
// Temporal Analysis & Occupancy
// ═══════════════════════════════════════════

function setupTimeControls() {
    const slider = document.getElementById('timeSlider');
    const daySelect = document.getElementById('daySelector');
    const playBtn = document.getElementById('playPauseBtn');

    slider.addEventListener('input', (e) => {
        currentTimeMinutes = parseInt(e.target.value);
        updateTimeDisplay();
        updateOccupancyHeatmap();
    });

    daySelect.addEventListener('change', (e) => {
        currentDayFilter = e.target.value;
        document.getElementById('currentDay').textContent = daySelect.options[daySelect.selectedIndex].text;

        // Sync schedule dropdown
        const scheduleDaySelect = document.getElementById('scheduleDaySelect');
        if (scheduleDaySelect) scheduleDaySelect.value = currentDayFilter;

        updateOccupancyHeatmap();
        renderMySchedule();
    });

    playBtn.addEventListener('click', () => {
        isPlaying = !isPlaying;
        if (isPlaying) {
            playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M14,19H18V5H14M6,19H10V5H6V19Z" /></svg>';
            playInterval = setInterval(() => {
                currentTimeMinutes += 5;
                if (currentTimeMinutes > 1320) currentTimeMinutes = 360;
                slider.value = currentTimeMinutes;
                updateTimeDisplay();
                updateOccupancyHeatmap();
            }, 300);
        } else {
            playBtn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M8,5.14V19.14L19,12.14L8,5.14Z" /></svg>';
            clearInterval(playInterval);
        }
    });

    updateTimeDisplay();
}

function updateTimeDisplay() {
    const h = Math.floor(currentTimeMinutes / 60);
    const m = currentTimeMinutes % 60;
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 || 12;
    document.getElementById('currentTime').textContent = `${h12}:${m.toString().padStart(2, '0')} ${ampm}`;
}

function updateOccupancyHeatmap() {
    if (!buildingsData || !scheduleData) return;

    // Compute currently active classes per building
    const occupancyData = {};

    scheduleData.forEach(course => {
        if (!course.days.includes(currentDayFilter)) return;

        const start = timeToMinutes(course.startTime);
        const end = timeToMinutes(course.endTime);

        if (currentTimeMinutes >= start && currentTimeMinutes <= end) {
            if (!occupancyData[course.building]) {
                occupancyData[course.building] = { enrolled: 0, capacity: 0 };
            }
            occupancyData[course.building].enrolled += course.enrollment;
            occupancyData[course.building].capacity += course.capacity;
        }
    });

    const entries = Object.entries(occupancyData);

    // If no active classes, revert to default height-based coloring
    if (entries.length === 0) {
        if (map.getLayer('buildings-3d')) {
            map.setPaintProperty('buildings-3d', 'fill-extrusion-color', buildingColorStops);
        }
        return;
    }

    // Build a valid MapLibre 'case' expression: ['case', cond1, val1, cond2, val2, ..., fallback]
    const colorExpr = ['case'];

    entries.forEach(([bName, data]) => {
        const ratio = data.capacity > 0 ? data.enrolled / data.capacity : 0;
        let color;
        if (ratio > 0.8) color = '#ef4444';
        else if (ratio > 0.6) color = '#f97316';
        else if (ratio > 0.4) color = '#fbbf24';
        else if (ratio > 0.2) color = '#3d8cf0';
        else color = '#3d5a9e';

        colorExpr.push(['==', ['get', 'display_name'], bName]);
        colorExpr.push(color);
    });

    colorExpr.push('#2a3a6b'); // Fallback: simple string (not a nested expression)

    if (map.getLayer('buildings-3d')) {
        map.setPaintProperty('buildings-3d', 'fill-extrusion-color', colorExpr);
    }
}

function timeToMinutes(timeStr) {
    const [h, m] = timeStr.split(':').map(Number);
    return h * 60 + m;
}

// ═══════════════════════════════════════════
// Course Schedule UI
// ═══════════════════════════════════════════

function setupCourseScheduleUI() {
    const input = document.getElementById('courseSearchInput');
    const results = document.getElementById('courseSearchResults');
    const clearBtn = document.getElementById('clearScheduleBtn');
    const routeBtn = document.getElementById('showRouteBtn');

    input.addEventListener('input', (e) => {
        const q = e.target.value.trim().toLowerCase();
        if (!q || !scheduleData) {
            results.innerHTML = '';
            results.classList.add('hidden');
            return;
        }

        const hits = scheduleData.filter(c =>
            c.id.toLowerCase().includes(q) ||
            c.title.toLowerCase().includes(q) ||
            c.department.toLowerCase().includes(q) ||
            c.building.toLowerCase().includes(q)
        ).slice(0, 8);

        if (hits.length > 0) {
            results.innerHTML = hits.map(c => `
                <div class="course-item" data-id="${c.id}">
                    <div style="font-weight:600">${c.title}</div>
                    <div class="course-meta">
                        <span>${c.building} · rm ${c.room}</span>
                        <span>${c.days.join('')} ${c.startTime}</span>
                    </div>
                </div>
            `).join('');
            results.classList.remove('hidden');
        } else {
            results.innerHTML = '<div class="course-item">No courses found</div>';
        }
    });

    results.addEventListener('click', (e) => {
        const item = e.target.closest('.course-item');
        if (!item || !item.dataset.id) return;

        const courseId = item.dataset.id;
        const course = scheduleData.find(c => c.id === courseId);

        if (course && !mySchedule.find(c => c.id === courseId)) {
            mySchedule.push(course);
            renderMySchedule();
            // Fly to building
            const b = buildingsData.features.find(f => f.properties.display_name === course.building);
            if (b) {
                const c = getCentroid(b.geometry);
                map.flyTo({ center: c, zoom: 17, pitch: 60 });
            }
        }

        input.value = '';
        results.innerHTML = '';
        results.classList.add('hidden');
    });

    clearBtn.addEventListener('click', () => {
        mySchedule = [];
        renderMySchedule();
        if (map.getSource('route')) {
            map.getSource('route').setData({ type: 'FeatureCollection', features: [] });
        }
        if (window._routeMarkers) {
            window._routeMarkers.forEach(m => m.remove());
            window._routeMarkers = [];
        }
    });

    routeBtn.addEventListener('click', showWalkingRoute);

    const scheduleDaySelect = document.getElementById('scheduleDaySelect');

    scheduleDaySelect.addEventListener('change', (e) => {
        currentDayFilter = e.target.value;

        // Sync global controls
        document.getElementById('daySelector').value = currentDayFilter;
        document.getElementById('currentDay').textContent = scheduleDaySelect.options[scheduleDaySelect.selectedIndex].text;

        updateOccupancyHeatmap();
        renderMySchedule();
    });

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.innerHTML = '';
            results.classList.add('hidden');
        }
    });
}

function renderMySchedule() {
    const list = document.getElementById('myScheduleList');
    const clearBtn = document.getElementById('clearScheduleBtn');
    const routeBtn = document.getElementById('showRouteBtn');

    if (mySchedule.length === 0) {
        list.innerHTML = '<p class="empty-msg">No courses added yet.</p>';
        clearBtn.classList.add('hidden');
        routeBtn.classList.add('hidden');
        const scheduleDaySelect = document.getElementById('scheduleDaySelect');
        if (scheduleDaySelect) scheduleDaySelect.style.display = 'none';
        return;
    }

    clearBtn.classList.remove('hidden');
    routeBtn.classList.remove('hidden');

    // Sort by day order then by start time
    const dayOrder = { Mon: 0, Tue: 1, Wed: 2, Thu: 3, Fri: 4, Sat: 5, Sun: 6 };
    const sorted = [...mySchedule].sort((a, b) => {
        const dayA = Math.min(...a.days.map(d => dayOrder[d] ?? 7));
        const dayB = Math.min(...b.days.map(d => dayOrder[d] ?? 7));
        if (dayA !== dayB) return dayA - dayB;
        return timeToMinutes(a.startTime) - timeToMinutes(b.startTime);
    });

    list.innerHTML = sorted.map(c => `
        <div class="scheduled-course">
            <span class="remove-course" onclick="removeCourse('${c.id}')">&times;</span>
            <div class="course-title">${c.title}</div>
            <div class="course-meta">
                <span>${c.building} · ${c.days.join(', ')}</span>
                <span>${c.startTime} – ${c.endTime}</span>
            </div>
        </div>
    `).join('');

    // Update route button text to be generic, as the dropdown above it shows the day
    routeBtn.textContent = `🚶 Show Route`;

    // Show/hide the schedule day selector
    const scheduleDaySelect = document.getElementById('scheduleDaySelect');
    if (scheduleDaySelect) {
        scheduleDaySelect.style.display = 'block';
        scheduleDaySelect.value = currentDayFilter;
    }
}

window.removeCourse = (id) => {
    mySchedule = mySchedule.filter(c => c.id !== id);
    renderMySchedule();
};

async function showWalkingRoute() {
    if (mySchedule.length < 2) return;

    // Filter to the currently selected day, then sort by start time
    const dayFiltered = mySchedule.filter(c => c.days.includes(currentDayFilter));
    if (dayFiltered.length < 2) {
        const dayNames = { Mon: 'Monday', Tue: 'Tuesday', Wed: 'Wednesday', Thu: 'Thursday', Fri: 'Friday' };
        alert(`You have fewer than 2 classes on ${dayNames[currentDayFilter] || currentDayFilter}. Switch the day selector or add more courses for that day.`);
        return;
    }
    const sorted = dayFiltered.sort((a, b) => timeToMinutes(a.startTime) - timeToMinutes(b.startTime));

    // Deduplicate consecutive buildings (skip if same building back-to-back)
    const waypoints = [];
    sorted.forEach(course => {
        const b = buildingsData.features.find(f => f.properties.display_name === course.building);
        if (b) {
            const coord = getCentroid(b.geometry);
            if (waypoints.length === 0 || waypoints[waypoints.length - 1].name !== course.building) {
                waypoints.push({ coord, name: course.building, time: course.startTime });
            }
        }
    });

    if (waypoints.length < 2) {
        alert('All your classes on this day are in the same building — no walking route needed!');
        return;
    }

    // Build OSRM request — foot profile, full geometry as GeoJSON
    const coordStr = waypoints.map(w => `${w.coord[0]},${w.coord[1]}`).join(';');
    const osrmUrl = `https://router.project-osrm.org/route/v1/foot/${coordStr}?overview=full&geometries=geojson&steps=true`;

    let routeGeometry;
    try {
        const res = await fetch(osrmUrl);
        const data = await res.json();
        if (data.code === 'Ok' && data.routes && data.routes.length > 0) {
            routeGeometry = data.routes[0].geometry;
        } else {
            console.warn('OSRM returned no route, falling back to straight line');
            routeGeometry = { type: 'LineString', coordinates: waypoints.map(w => w.coord) };
        }
    } catch (e) {
        console.warn('OSRM request failed, falling back to straight line:', e.message);
        routeGeometry = { type: 'LineString', coordinates: waypoints.map(w => w.coord) };
    }

    const routeGeoJSON = { type: 'Feature', properties: {}, geometry: routeGeometry };

    // Remove old waypoint markers
    if (window._routeMarkers) {
        window._routeMarkers.forEach(m => m.remove());
    }
    window._routeMarkers = [];

    // Draw the route line
    if (!map.getSource('route')) {
        map.addSource('route', { type: 'geojson', data: routeGeoJSON });
        map.addLayer({
            id: 'route-line',
            type: 'line',
            source: 'route',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: { 'line-color': '#fbbf24', 'line-width': 5, 'line-opacity': 0.85 }
        });
    } else {
        map.getSource('route').setData(routeGeoJSON);
    }

    // Add numbered waypoint markers with time info
    waypoints.forEach((wp, i) => {
        const el = document.createElement('div');
        el.className = 'route-marker';
        el.textContent = i + 1;
        const popupText = wp.time ? `${i + 1}. ${wp.name} (${wp.time})` : `${i + 1}. ${wp.name}`;
        const marker = new maplibregl.Marker({ element: el })
            .setLngLat(wp.coord)
            .setPopup(new maplibregl.Popup({ offset: 25 }).setText(popupText))
            .addTo(map);
        window._routeMarkers.push(marker);
    });

    // Fit map to route
    const bounds = new maplibregl.LngLatBounds();
    routeGeometry.coordinates.forEach(c => bounds.extend(c));
    map.fitBounds(bounds, { padding: 80, pitch: 50 });
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

    // Add Building Specific Analytics
    const bName = props._name || props.display_name;
    if (type === 'building' && bName && scheduleData) {
        const buildingClasses = scheduleData.filter(c => c.building === bName);
        if (buildingClasses.length > 0) {
            const chartHtml = `
                <div class="mt-4">
                    <h3 class="panel-sub-title">Today's Classes (${buildingClasses.length})</h3>
                    <div style="font-size:11px; max-height:120px; overflow-y:auto; margin-bottom:12px;">
                        ${buildingClasses.map(c => `
                            <div style="padding:4px 0; border-bottom:1px solid var(--border)">
                                <b>${c.id}</b>: ${c.startTime} – ${c.endTime}
                            </div>
                        `).join('')}
                    </div>
                    <h3 class="panel-sub-title">Occupancy Timeline</h3>
                    <div style="position:relative; height:130px; width:100%; margin-bottom:12px;">
                        <canvas id="bldgTimelineChart"></canvas>
                    </div>
                    <h3 class="panel-sub-title">Room Utilization</h3>
                    <div style="position:relative; height:130px; width:100%;">
                        <canvas id="bldgUtilityChart"></canvas>
                    </div>
                </div>
            `;
            info.insertAdjacentHTML('beforeend', chartHtml);

            // Build mini charts for this building after DOM updates
            setTimeout(() => buildBuildingMiniCharts(bName, buildingClasses), 150);
        }
    }
}

function buildBuildingMiniCharts(bName, classes) {
    const timelineCtx = document.getElementById('bldgTimelineChart')?.getContext('2d');
    const utilityCtx = document.getElementById('bldgUtilityChart')?.getContext('2d');
    if (!timelineCtx || !utilityCtx) return;

    // Timeline: 7 AM to 9 PM
    const hours = Array.from({ length: 15 }, (_, i) => i + 7);
    const hourlyOccupancy = hours.map(h => {
        const time = h * 60;
        const active = classes.filter(c => {
            const s = timeToMinutes(c.startTime);
            const e = timeToMinutes(c.endTime);
            return time >= s && time <= e;
        });
        const totalEnrolled = active.reduce((sum, c) => sum + c.enrollment, 0);
        const totalCapacity = active.reduce((sum, c) => sum + c.capacity, 0);
        return totalCapacity > 0 ? (totalEnrolled / totalCapacity) * 100 : 0;
    });

    new Chart(timelineCtx, {
        type: 'line',
        data: {
            labels: hours.map(h => h > 12 ? (h - 12) + 'PM' : h + 'AM'),
            datasets: [{
                data: hourlyOccupancy,
                borderColor: '#fbbf24',
                backgroundColor: 'rgba(251, 191, 36, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, ticks: { display: false }, grid: { display: false } },
                x: { ticks: { font: { size: 8 }, color: '#5a5e76' }, grid: { display: false } }
            }
        }
    });

    const totalRooms = 12; // Mock building room count
    const occupiedRooms = new Set(classes.map(c => c.room)).size;

    new Chart(utilityCtx, {
        type: 'doughnut',
        data: {
            labels: ['Occupied', 'Available'],
            datasets: [{
                data: [occupiedRooms, totalRooms - occupiedRooms],
                backgroundColor: ['#ef4444', '#1e2235'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: { legend: { display: false } }
        }
    });
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
    buildGlobalActivityCharts();
}

function buildGlobalActivityCharts() {
    if (!scheduleData) return;

    // 1. Day Distribution Heatmap
    const daysOrder = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const dayLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const countsPerDay = daysOrder.map(d => scheduleData.filter(c => c.days.includes(d)).length);

    const dayCtx = document.getElementById('dayActivityChart')?.getContext('2d');
    if (dayCtx) {
        new Chart(dayCtx, {
            type: 'bar',
            data: {
                labels: dayLabels,
                datasets: [{
                    label: 'Classes',
                    data: countsPerDay,
                    backgroundColor: 'rgba(56, 189, 248, 0.7)',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#5a5e76', font: { size: 9 } }, grid: { display: false } },
                    y: { ticks: { color: '#5a5e76', font: { size: 9 } }, grid: { color: 'rgba(30,34,53,0.5)' } }
                }
            }
        });
    }

    // 2. Busiest Buildings
    const bldgCounts = {};
    scheduleData.forEach(c => {
        bldgCounts[c.building] = (bldgCounts[c.building] || 0) + 1;
    });

    const sortedBldgs = Object.entries(bldgCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);

    const bldgCtx = document.getElementById('busiestBuildingsChart')?.getContext('2d');
    if (bldgCtx) {
        new Chart(bldgCtx, {
            type: 'bar',
            data: {
                labels: sortedBldgs.map(b => b[0]),
                datasets: [{
                    data: sortedBldgs.map(b => b[1]),
                    backgroundColor: '#a78bfa',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#5a5e76', font: { size: 9 } }, grid: { color: 'rgba(30,34,53,0.5)' } },
                    y: { ticks: { color: '#5a5e76', font: { size: 8 } }, grid: { display: false } }
                }
            }
        });
    }
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
