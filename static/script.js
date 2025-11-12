/*
Story Time Locator - Frontend JavaScript (Rewritten for Local Data)

NEW APPROACH: No external APIs!
This file now handles:
1. Form submission with simplified inputs
2. Communication with our Flask backend (which uses local JSON data)
3. Displaying story time events from Jersey City and Hoboken libraries
4. Error handling
*/

// Global function to expand popup events (called from onclick in popup HTML)
window.expandPopupEvents = function(popupId) {
    const hiddenContainer = document.getElementById(`${popupId}-hidden`);
    const button = document.getElementById(`${popupId}-btn`);

    if (hiddenContainer && button) {
        hiddenContainer.classList.add('expanded');
        button.style.display = 'none';
    }
};

// Wait for the page to fully load before running code
// This ensures all HTML elements exist before we try to access them
document.addEventListener('DOMContentLoaded', function() {

    // Get references to HTML elements we'll need
    const form = document.getElementById('searchForm');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    const results = document.getElementById('results');
    const viewToggle = document.getElementById('viewToggle');
    const listViewBtn = document.getElementById('listViewBtn');
    const mapViewBtn = document.getElementById('mapViewBtn');
    const mapContainer = document.getElementById('mapContainer');

    // Map-related variables
    let map = null;
    let markers = [];
    let markerClusterGroup = null;
    let currentEvents = [];
    let locationsData = {};

    // Load location data on page load
    async function loadLocationData() {
        try {
            const response = await fetch('/locations');
            locationsData = await response.json();
        } catch (err) {
            console.error('Failed to load location data:', err);
        }
    }
    loadLocationData();

    // Listen for form submission
    form.addEventListener('submit', async function(e) {
        // Prevent default form submission (which would reload the page)
        e.preventDefault();

        // Hide any previous errors or results
        hideError();
        results.innerHTML = '';

        // Show loading indicator
        loading.classList.remove('hidden');

        // Collect form data
        const formData = new FormData(form);

        // Get selected days (multiple checkboxes)
        const selectedDays = [];
        formData.getAll('days').forEach(day => {
            selectedDays.push(day);
        });

        // Get selected times of day (multiple checkboxes)
        const selectedTimes = [];
        formData.getAll('time_of_day').forEach(time => {
            selectedTimes.push(time);
        });

        // Build request data
        const data = {
            city: formData.get('city'),
            branches: selectedBranches,  // Changed from 'branch' to 'branches' array
            kids_ages: formData.get('kids_ages') || '',
            venue_type: formData.get('venue_type') || 'all',
            event_type: formData.get('event_type') || 'all',
            date_range: formData.get('date_range') || 'all',
            days: selectedDays,
            time_of_day: selectedTimes
        };

        // Track the search event in Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search', {
                'event_category': 'Story Time Search',
                'event_label': data.city,
                'city': data.city,
                'event_type': data.event_type,
                'has_age_filter': data.kids_ages ? 'yes' : 'no',
                'has_branch_filter': data.branches.length > 0 ? 'yes' : 'no'
            });
        }

        try {
            // Send POST request to backend
            // Our backend filters the local JSON data based on these preferences
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            // Check if request was successful
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Search failed');
            }

            // Parse JSON response from backend
            const responseData = await response.json();

            // Hide loading indicator
            loading.classList.add('hidden');

            // Store current events for map view
            currentEvents = responseData.results;

            // Show view toggle buttons
            if (currentEvents.length > 0) {
                viewToggle.classList.remove('hidden');
            }

            // Check if user is currently in map view
            const isMapViewActive = mapViewBtn.classList.contains('active');

            // Display results (default to list view)
            displayResults(responseData);

            // If map view is active, update the map with new results
            if (isMapViewActive && currentEvents.length > 0) {
                initializeMap();
            }

        } catch (err) {
            // Hide loading indicator
            loading.classList.add('hidden');

            // Show error message to user
            showError(err.message || 'An error occurred. Please try again.');
        }
    });

    /**
     * Strip HTML tags from a string
     * This prevents HTML in event descriptions from breaking our card layout
     *
     * @param {string} html - String potentially containing HTML
     * @returns {string} Plain text without HTML tags
     */
    function stripHtml(html) {
        if (!html) return '';
        const doc = new DOMParser().parseFromString(html, 'text/html');
        return doc.body.textContent || '';
    }

    /**
     * Display search results
     *
     * Takes the filtered event data and creates HTML to show the results
     *
     * @param {Object} data - Response from backend containing results array
     */
    function displayResults(data) {
        const events = data.results;

        // Check if we got any results
        if (!events || events.length === 0) {
            results.innerHTML = `
                <div class="no-results">
                    <p>😔 No story times found matching your criteria.</p>
                    <p>Try adjusting your filters or selecting "Both Cities" to see more options.</p>
                </div>
            `;
            return;
        }

        // Create header showing number of results
        const cityName = getCityDisplayName(data.user_preferences.city);
        let html = `
            <h2 class="results-header">
                📚 Found ${events.length} Story Time${events.length !== 1 ? 's' : ''} in ${cityName}
            </h2>
        `;

        // Create a card for each event
        events.forEach((event, index) => {
            html += createEventCard(event, index + 1);
        });

        // Insert the HTML into the results div
        results.innerHTML = html;

        // Smooth scroll to results
        results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Create HTML for a single event card
     *
     * @param {Object} event - Event data from our JSON files
     * @param {number} number - Position in results (1, 2, 3, etc.)
     * @returns {string} HTML string for the card
     */
    function createEventCard(event, number) {
        // Format the date nicely
        const formattedDate = formatEventDate(event.date, event.day_of_week);

        // Get city name (if available)
        const cityBadge = event.city
            ? `<span class="city-badge">${event.city}</span>`
            : '';

        // Check if event is FREE
        // Events are free if:
        // 1. Title contains "(FREE)" OR
        // 2. It's NOT a Little City Books story time (they charge a small fee)
        const titleLower = (event.title || '').toLowerCase();
        const venueLower = (event.venue_name || event.location || '').toLowerCase();
        const isFree = titleLower.includes('(free)') ||
                      !(venueLower.includes('little city') && titleLower.includes('story time'));
        const freeBadge = isFree ? `<span class="free-badge">FREE</span>` : '';

        // Get venue/branch info
        // For bookstores, use venue_name; for libraries, use branch
        const venue = event.venue_name || event.branch || event.location || 'Library';

        // Get audience/age range
        const audienceInfo = event.audience
            ? `<div class="event-audience">👶 ${event.audience}</div>`
            : '';

        // Build time display (with end time if it's a long event)
        let timeDisplay = `📅 ${formattedDate} at ${event.formatted_time}`;
        if (event.formatted_end_time && event.duration_hours > 1) {
            timeDisplay += ` - ${event.formatted_end_time}`;
        }

        // Add all-day badge if applicable
        const allDayBadge = event.is_all_day
            ? `<span class="all-day-badge">🕐 All Day Event (Drop-in anytime)</span>`
            : '';

        // Build description (strip HTML first, then truncate if too long)
        const rawDescription = event.description || event.full_description || '';
        const cleanDescription = stripHtml(rawDescription);
        const truncatedDescription = cleanDescription.length > 200
            ? cleanDescription.substring(0, 200) + '...'
            : cleanDescription;

        return `
            <div class="result-card event-card">
                <div class="event-badges">
                    ${cityBadge}
                    ${freeBadge}
                </div>
                <div class="event-title">
                    📖 ${stripHtml(event.title)}
                </div>

                <div class="event-datetime">
                    ${timeDisplay}
                </div>

                ${allDayBadge ? `<div class="event-datetime">${allDayBadge}</div>` : ''}

                <div class="event-location">
                    📍 ${venue}
                </div>

                ${audienceInfo}

                ${truncatedDescription ? `<div class="event-description">${truncatedDescription}</div>` : ''}

                <div class="event-actions">
                    <a href="${event.link}" target="_blank" rel="noopener" class="event-link">
                        ℹ️ View Details & Register
                    </a>
                </div>
            </div>
        `;
    }

    /**
     * Format event date for display
     *
     * @param {string} dateStr - Date in YYYY-MM-DD format
     * @param {string} dayOfWeek - Day name
     * @returns {string} Formatted date like "Saturday, Oct 28"
     */
    function formatEventDate(dateStr, dayOfWeek) {
        try {
            const date = new Date(dateStr + 'T00:00:00');
            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

            const month = monthNames[date.getMonth()];
            const day = date.getDate();

            return `${dayOfWeek}, ${month} ${day}`;
        } catch (e) {
            // If date parsing fails, return the original
            return `${dayOfWeek}, ${dateStr}`;
        }
    }

    /**
     * Get display name for city selection
     *
     * @param {string} cityValue - City value from form
     * @returns {string} Display name
     */
    function getCityDisplayName(cityValue) {
        switch(cityValue) {
            case 'jersey_city':
                return 'Jersey City';
            case 'hoboken':
                return 'Hoboken';
            case 'both':
                return 'Jersey City & Hoboken';
            default:
                return cityValue;
        }
    }

    /**
     * Show error message to user
     *
     * @param {string} message - Error message to display
     */
    function showError(message) {
        errorMessage.textContent = message;
        error.classList.remove('hidden');

        // Scroll to error message
        error.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Hide error message
     */
    function hideError() {
        error.classList.add('hidden');
        errorMessage.textContent = '';
    }

    /**
     * Handle city selection change - update branch options based on city
     */
    const citySelect = document.getElementById('city');
    const branchDropdownHeader = document.getElementById('branchDropdownHeader');
    const branchDropdownOptions = document.getElementById('branchDropdownOptions');
    const branchSelectedText = document.getElementById('branchSelectedText');

    // Track selected branches
    let selectedBranches = [];

    // Function to update the selected text display
    function updateSelectedText() {
        if (selectedBranches.length === 0) {
            branchSelectedText.textContent = 'Select locations...';
        } else if (selectedBranches.length === 1) {
            branchSelectedText.textContent = selectedBranches[0];
        } else {
            branchSelectedText.textContent = `${selectedBranches.length} locations selected`;
        }
    }

    // Function to load branches for a given city
    async function loadBranches(city) {
        try {
            let allGroups = [];

            if (city === 'both') {
                // Load branches from both cities
                const jcResponse = await fetch('/branches/jersey_city');
                const jcData = await jcResponse.json();
                const hobokenResponse = await fetch('/branches/hoboken');
                const hobokenData = await hobokenResponse.json();

                // Combine groups from both cities
                allGroups = [
                    ...(jcData.groups || []).map(g => ({...g, label: `JC - ${g.label}`})),
                    ...(hobokenData.groups || []).map(g => ({...g, label: `Hoboken - ${g.label}`}))
                ];
            } else {
                // Load branches for specific city
                const response = await fetch(`/branches/${city}`);
                const data = await response.json();
                allGroups = data.groups || [];
            }

            // Clear existing options and rebuild
            branchDropdownOptions.innerHTML = '';

            // Add branch options with groups and checkboxes
            allGroups.forEach(group => {
                // Add group label
                const groupLabel = document.createElement('div');
                groupLabel.className = 'multiselect-group-label';
                groupLabel.textContent = group.label;
                branchDropdownOptions.appendChild(groupLabel);

                // Add branches in this group
                group.branches.forEach(branch => {
                    const optionDiv = document.createElement('div');
                    optionDiv.className = 'multiselect-option';

                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `branch-${branch.replace(/\s+/g, '-')}`;
                    checkbox.value = branch;
                    checkbox.checked = selectedBranches.includes(branch);

                    const label = document.createElement('label');
                    label.htmlFor = checkbox.id;
                    label.textContent = branch;

                    // Handle checkbox change
                    checkbox.addEventListener('change', function() {
                        if (this.checked) {
                            if (!selectedBranches.includes(branch)) {
                                selectedBranches.push(branch);
                            }
                        } else {
                            selectedBranches = selectedBranches.filter(b => b !== branch);
                        }
                        updateSelectedText();
                    });

                    optionDiv.appendChild(checkbox);
                    optionDiv.appendChild(label);
                    branchDropdownOptions.appendChild(optionDiv);
                });
            });

        } catch (err) {
            console.error('Failed to load branches:', err);
            branchDropdownOptions.innerHTML = '';
        }
    }

    // Toggle dropdown open/close
    branchDropdownHeader.addEventListener('click', function() {
        const isOpen = branchDropdownOptions.style.display === 'block';
        branchDropdownOptions.style.display = isOpen ? 'none' : 'block';
        branchDropdownHeader.classList.toggle('active', !isOpen);
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.custom-multiselect')) {
            branchDropdownOptions.style.display = 'none';
            branchDropdownHeader.classList.remove('active');
        }
    });

    // Load branches on page load (default is "both" cities)
    loadBranches('both');

    // Update branches when city selection changes
    citySelect.addEventListener('change', async function() {
        const selectedCity = citySelect.value;
        selectedBranches = []; // Clear selections
        updateSelectedText();
        await loadBranches(selectedCity);
    });

    /**
     * Clear all filters and reset form to defaults
     */
    const clearFiltersBtn = document.getElementById('clearFilters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            // Reset all form fields to defaults
            document.getElementById('city').value = 'both';
            document.getElementById('kids_ages').value = '';
            document.getElementById('venue_type').value = 'all';
            document.getElementById('event_type').value = 'all';
            document.getElementById('date_range').value = '2weeks';

            // Reset branch filter and reload all branches
            selectedBranches = [];
            updateSelectedText();
            loadBranches('both');

            // Uncheck all day checkboxes
            document.querySelectorAll('input[name="days"]').forEach(checkbox => {
                checkbox.checked = false;
            });

            // Check all time of day checkboxes (default state)
            document.querySelectorAll('input[name="time_of_day"]').forEach(checkbox => {
                checkbox.checked = true;
            });

            // Clear results and errors
            results.innerHTML = '';
            hideError();

            // Hide view toggle and reset to list view
            viewToggle.classList.add('hidden');
            switchToListView();
        });
    }

    /**
     * Get neighborhood for a venue (for display on map)
     */
    function getNeighborhood(venueName) {
        // Jersey City neighborhood mapping
        const jcNeighborhoods = {
            'Downtown': ['Pavonia Branch', 'Priscilla Gardner Main Library', 'WORD Bookstore'],
            'Heights': ['Heights Branch'],
            'Greenville': ['Earl A. Morgan Branch (Greenville)'],
            'Journal Square': ['Five Corners Branch'],
            'West Side': ['Marion Branch', 'West Bergen Branch'],
            'Bergen-Lafayette': ['Communipaw Branch'],
            'The Hill': ['Glenn D. Cunningham Branch'],
            'McGinley Square': ['Miller Branch']
        };

        // Hoboken (single neighborhood)
        const hobokenLocations = ['Hoboken Public Library', 'Hoboken Public Library - Grand Street Branch', 'Little City Books'];

        // Check Jersey City neighborhoods
        for (let neighborhood in jcNeighborhoods) {
            if (jcNeighborhoods[neighborhood].some(loc => venueName.includes(loc) || loc.includes(venueName))) {
                return `JC - ${neighborhood}`;
            }
        }

        // Check Hoboken
        if (hobokenLocations.some(loc => venueName.includes(loc) || loc.includes(venueName))) {
            return 'Hoboken';
        }

        return null;
    }

    /**
     * Add floating legend to map
     */
    function addMapLegend() {
        const legendHTML = `
            <div class="map-legend">
                <div class="legend-header" id="legendHeader">
                    <span>Map Legend</span>
                    <span class="legend-toggle" id="legendToggle">−</span>
                </div>
                <div class="legend-body" id="legendBody">
                    <div class="legend-section">
                        <div class="legend-section-title">Venue Type</div>
                        <div class="legend-item">
                            <div class="legend-color-box library"></div>
                            <span>Libraries</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color-box bookstore"></div>
                            <span>Bookstores</span>
                        </div>
                    </div>
                    <div class="legend-section">
                        <div class="legend-section-title">Event Count</div>
                        <div class="legend-size-demo">
                            <div class="legend-pin-small">3</div>
                            <span style="font-size: 12px; color: #666;">1-3 events</span>
                        </div>
                        <div class="legend-size-demo">
                            <div class="legend-pin-medium">7</div>
                            <span style="font-size: 12px; color: #666;">4-10 events</span>
                        </div>
                        <div class="legend-size-demo">
                            <div class="legend-pin-large">15</div>
                            <span style="font-size: 12px; color: #666;">10+ events</span>
                        </div>
                    </div>
                    <div class="legend-section">
                        <div style="font-size: 11px; color: #888; font-style: italic; line-height: 1.4;">
                            💡 Hover over pins to see neighborhood. Click for event details.
                        </div>
                        <div style="font-size: 11px; color: #888; font-style: italic; line-height: 1.4; margin-top: 8px;">
                            🔍 Zoom out to see nearby locations grouped together. Click clusters to zoom in.
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add legend to map container
        const mapContainer = document.getElementById('map');
        const existingLegend = mapContainer.querySelector('.map-legend');
        if (!existingLegend) {
            mapContainer.insertAdjacentHTML('beforeend', legendHTML);

            // Add toggle functionality
            const legendHeader = document.getElementById('legendHeader');
            const legendBody = document.getElementById('legendBody');
            const legendToggle = document.getElementById('legendToggle');

            legendHeader.addEventListener('click', function() {
                legendBody.classList.toggle('collapsed');
                legendToggle.textContent = legendBody.classList.contains('collapsed') ? '+' : '−';
            });
        }
    }

    /**
     * Initialize map view with event markers
     */
    function initializeMap() {
        // Create map if it doesn't exist
        if (!map) {
            // Center map on Jersey City/Hoboken area
            map = L.map('map').setView([40.7282, -74.0445], 13);

            // Add CartoDB Positron tiles (free, no API key needed, cleaner design!)
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(map);

            // Configure map for better mobile behavior
            map.on('popupopen', function(e) {
                // Prevent map from auto-zooming when popup opens on mobile
                const px = map.project(e.popup._latlng);
                px.y -= e.popup._container.clientHeight / 2;
                map.panTo(map.unproject(px), { animate: true });
            });

            // Enable touch scrolling on mobile
            if (window.innerWidth <= 768) {
                map.dragging.enable();
                map.touchZoom.enable();
                map.scrollWheelZoom.enable();
            }

            // Add legend to map
            addMapLegend();

            // Initialize marker cluster group with mobile-friendly settings
            markerClusterGroup = L.markerClusterGroup({
                maxClusterRadius: 60,
                spiderfyOnMaxZoom: true,
                showCoverageOnHover: false,
                zoomToBoundsOnClick: true,
                disableClusteringAtZoom: 17, // Disable clustering when zoomed in close
                spiderfyDistanceMultiplier: 2, // More space between spiderfied markers on mobile
                animate: true,
                animateAddingMarkers: false,
                removeOutsideVisibleBounds: false, // Keep markers in memory for smoother interaction
                iconCreateFunction: function(cluster) {
                    const childCount = cluster.getChildCount();
                    let sizeClass = 'marker-cluster-small';
                    if (childCount > 10) {
                        sizeClass = 'marker-cluster-large';
                    } else if (childCount > 5) {
                        sizeClass = 'marker-cluster-medium';
                    }
                    return L.divIcon({
                        html: '<div>' + childCount + '</div>',
                        className: 'marker-cluster ' + sizeClass,
                        iconSize: L.point(40, 40)
                    });
                }
            });

            // Handle cluster click to ensure proper zoom behavior on mobile
            markerClusterGroup.on('clusterclick', function (a) {
                // On mobile, zoom in and re-enable dragging
                if (window.innerWidth <= 768) {
                    a.layer.zoomToBounds({ padding: [50, 50] });
                    // Re-enable dragging after cluster click
                    setTimeout(function() {
                        map.dragging.enable();
                    }, 100);
                }
            });

            map.addLayer(markerClusterGroup);
        }

        // Clear existing markers
        markers.forEach(marker => markerClusterGroup.removeLayer(marker));
        markers = [];
        markerClusterGroup.clearLayers();

        // Group events by location
        const eventsByLocation = {};
        currentEvents.forEach(event => {
            // Get venue name (for matching with locations.json)
            const venueName = getVenueKey(event);
            if (!venueName) return;

            if (!eventsByLocation[venueName]) {
                eventsByLocation[venueName] = [];
            }
            eventsByLocation[venueName].push(event);
        });

        // Create markers for each location with events
        Object.keys(eventsByLocation).forEach(venueName => {
            const location = locationsData[venueName];
            if (!location || !location.lat || !location.lng) {
                console.warn(`No coordinates found for: ${venueName}`);
                return;
            }

            const eventsAtLocation = eventsByLocation[venueName];

            // Get neighborhood for this location
            const neighborhood = getNeighborhood(venueName);

            // Determine marker size based on event count
            const eventCount = eventsAtLocation.length;
            let sizeClass, iconSize, anchorY;
            if (eventCount <= 3) {
                sizeClass = 'pin-size-small';
                iconSize = [40, 52];  // width, height (includes pointer)
                anchorY = 52;  // Bottom of pointer
            } else if (eventCount <= 10) {
                sizeClass = 'pin-size-medium';
                iconSize = [50, 62];
                anchorY = 62;
            } else {
                sizeClass = 'pin-size-large';
                iconSize = [60, 72];
                anchorY = 72;
            }

            // Color based on venue type
            const colorClass = location.type === 'bookstore' ? 'pin-bookstore' : 'pin-library';

            // Create professional pin marker with event count
            const icon = L.divIcon({
                className: 'map-pin-marker-wrapper',
                html: `
                    <div class="map-pin-marker ${sizeClass}">
                        <div class="pin-circle ${colorClass}">
                            ${eventCount}
                        </div>
                        <div class="pin-pointer ${colorClass}"></div>
                    </div>
                `,
                iconSize: iconSize,
                iconAnchor: [iconSize[0] / 2, anchorY],
                popupAnchor: [0, -anchorY + 10]
            });

            // Create marker with tooltip showing neighborhood
            const marker = L.marker([location.lat, location.lng], { icon });

            // Add tooltip with neighborhood (shows on hover)
            if (neighborhood) {
                marker.bindTooltip(neighborhood, {
                    direction: 'top',
                    offset: [0, -10],
                    opacity: 0.9,
                    className: 'custom-tooltip'
                });
            }

            // Build improved popup content with visual hierarchy
            const venueTypeClass = location.type === 'bookstore' ? 'bookstore' : 'library';
            const popupId = `popup-${venueName.replace(/\s+/g, '-').replace(/[^\w-]/g, '')}`;

            let popupContent = `
                <div class="popup-header ${venueTypeClass}">
                    <div class="popup-header-title">${venueName}</div>
                    <div class="popup-header-subtitle">${neighborhood || location.city} • ${location.address}</div>
                </div>
                <div class="popup-body">
                    <div class="popup-event-count">📅 ${eventsAtLocation.length} Upcoming Event${eventsAtLocation.length !== 1 ? 's' : ''}</div>
            `;

            // Add first 3 events to popup (always visible)
            eventsAtLocation.slice(0, 3).forEach(event => {
                const formattedDate = formatEventDate(event.date, event.day_of_week);
                popupContent += `
                    <div class="popup-event-item ${venueTypeClass}">
                        <div class="popup-event-title">${stripHtml(event.title)}</div>
                        <div class="popup-event-time">📅 ${formattedDate} at ${event.formatted_time}</div>
                        <a href="${event.link}" target="_blank" rel="noopener" class="popup-event-link">
                            View Details & Register →
                        </a>
                    </div>
                `;
            });

            // If more than 3 events, add hidden container with remaining events
            if (eventsAtLocation.length > 3) {
                const remainingCount = eventsAtLocation.length - 3;
                popupContent += `<div class="popup-hidden-events" id="${popupId}-hidden">`;

                // Add remaining events (hidden initially)
                eventsAtLocation.slice(3).forEach(event => {
                    const formattedDate = formatEventDate(event.date, event.day_of_week);
                    popupContent += `
                        <div class="popup-event-item ${venueTypeClass}">
                            <div class="popup-event-title">${stripHtml(event.title)}</div>
                            <div class="popup-event-time">📅 ${formattedDate} at ${event.formatted_time}</div>
                            <a href="${event.link}" target="_blank" rel="noopener" class="popup-event-link">
                                View Details & Register →
                            </a>
                        </div>
                    `;
                });

                popupContent += `</div>`;

                // Add "Show All" button
                popupContent += `
                    <button class="popup-show-all-btn ${venueTypeClass}" id="${popupId}-btn" onclick="expandPopupEvents('${popupId}')">
                        Show ${remainingCount} More Event${remainingCount !== 1 ? 's' : ''} ↓
                    </button>
                `;
            }

            popupContent += `</div>`;

            // Configure popup with mobile-friendly settings
            const isMobile = window.innerWidth <= 768;
            marker.bindPopup(popupContent, {
                maxWidth: isMobile ? 300 : 350,
                minWidth: isMobile ? 250 : 280,
                maxHeight: isMobile ? window.innerHeight * 0.7 : 500, // 70% of screen height on mobile
                className: 'custom-popup',
                autoPan: isMobile ? false : true, // CRITICAL: Disable autoPan on mobile to prevent scroll bounce
                autoPanPadding: isMobile ? [20, 20] : [50, 50],
                closeButton: true,
                autoClose: false,
                keepInView: false // Disable keepInView on mobile to prevent repositioning
            });

            // Add touch event handlers to popup for mobile scrolling
            if (isMobile) {
                marker.on('popupopen', function(e) {
                    const popup = e.popup;
                    const popupElement = popup._container;
                    const popupBody = popupElement.querySelector('.popup-body');

                    if (popupBody) {
                        // Disable map dragging when touching popup content
                        // This prevents the map from moving when trying to scroll the popup
                        popupElement.addEventListener('touchstart', function(e) {
                            map.dragging.disable();
                            map.scrollWheelZoom.disable();
                        }, { passive: true });

                        popupElement.addEventListener('touchend', function(e) {
                            map.dragging.enable();
                            map.scrollWheelZoom.enable();
                        }, { passive: true });

                        // Enable smooth scrolling in popup body with proper touch handling
                        // Use passive: true to allow browser's native scroll optimization
                        popupBody.addEventListener('touchstart', function(e) {
                            // Don't propagate to map, but allow native scroll
                            e.stopPropagation();
                        }, { passive: true });

                        popupBody.addEventListener('touchmove', function(e) {
                            // CRITICAL: Use passive: true to allow smooth native scrolling
                            // Only stop propagation to prevent map from moving
                            e.stopPropagation();
                        }, { passive: true });

                        popupBody.addEventListener('touchend', function(e) {
                            e.stopPropagation();
                        }, { passive: true });
                    }
                });
            }

            // Add marker to cluster group
            markerClusterGroup.addLayer(marker);
            markers.push(marker);
        });

        // Fit map to show all markers
        if (markers.length > 0) {
            map.fitBounds(markerClusterGroup.getBounds().pad(0.1));
        }

        // Force map to refresh its size
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
    }

    /**
     * Get venue key for matching with locations.json
     */
    function getVenueKey(event) {
        // Try different fields to find the venue name
        // Priority: venue_name (bookstores), then calendar_source (libraries)
        let venueName = event.venue_name || event.calendar_source || event.location || event.branch;

        if (!venueName) return null;

        // Match against keys in locations.json
        // Try exact match first
        if (locationsData[venueName]) {
            return venueName;
        }

        // Try fuzzy matching (check if location key contains the venue name or vice versa)
        for (let key in locationsData) {
            if (key.toLowerCase().includes(venueName.toLowerCase()) ||
                venueName.toLowerCase().includes(key.toLowerCase())) {
                return key;
            }
        }

        return null;
    }

    /**
     * Switch to list view
     */
    function switchToListView() {
        listViewBtn.classList.add('active');
        mapViewBtn.classList.remove('active');
        results.classList.remove('hidden');
        mapContainer.classList.add('hidden');
    }

    /**
     * Switch to map view
     */
    function switchToMapView() {
        mapViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        results.classList.add('hidden');
        mapContainer.classList.remove('hidden');

        // Initialize map with current events
        initializeMap();
    }

    /**
     * Handle view toggle button clicks
     */
    listViewBtn.addEventListener('click', switchToListView);
    mapViewBtn.addEventListener('click', switchToMapView);

});
