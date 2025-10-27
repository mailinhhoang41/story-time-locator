/*
Story Time Locator - Frontend JavaScript (Rewritten for Local Data)

NEW APPROACH: No external APIs!
This file now handles:
1. Form submission with simplified inputs
2. Communication with our Flask backend (which uses local JSON data)
3. Displaying story time events from Jersey City and Hoboken libraries
4. Error handling
*/

// Wait for the page to fully load before running code
// This ensures all HTML elements exist before we try to access them
document.addEventListener('DOMContentLoaded', function() {

    // Get references to HTML elements we'll need
    const form = document.getElementById('searchForm');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    const results = document.getElementById('results');

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
            kids_ages: formData.get('kids_ages') || '',
            venue_type: formData.get('venue_type') || 'all',
            event_type: formData.get('event_type') || 'all',
            date_range: formData.get('date_range') || 'all',
            days: selectedDays,
            time_of_day: selectedTimes
        };

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

            // Display results
            displayResults(responseData);

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
                ${cityBadge}
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
        });
    }

});
