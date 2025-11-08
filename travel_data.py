"""
Travel History Data
Store travel periods for residence tracking

This file can be duplicated and customized for different people.
Just update the TRAVEL_HISTORY list with their travel dates.
"""

import datetime

# ============================================================================
# PERSONAL INFORMATION
# ============================================================================

PERSON_NAME = "Omer"  # Update this for different people
ANALYSIS_DATE = datetime.date(2025, 11, 8)  # Today's date
BUFFER_DAYS = 12  # Safety buffer (10-15 days recommended)

# ============================================================================
# TRAVEL HISTORY
# ============================================================================
# Format: {'country': 'Turkey' or 'Germany', 'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
# Keep periods in chronological order for easier reading

TRAVEL_HISTORY = [
    # ========================================
    # 2024 TRAVEL
    # ========================================
    {'country': 'Germany', 'start': '2024-09-15', 'end': '2024-11-04'},
    {'country': 'Turkey', 'start': '2024-11-04', 'end': '2024-11-21'},
    {'country': 'Germany', 'start': '2024-11-21', 'end': '2024-12-31'},

    # ========================================
    # 2025 TRAVEL
    # ========================================
    {'country': 'Germany', 'start': '2025-01-01', 'end': '2025-03-07'},
    {'country': 'Turkey', 'start': '2025-03-07', 'end': '2025-03-31'},
    {'country': 'Germany', 'start': '2025-04-01', 'end': '2025-04-22'},
    {'country': 'Turkey', 'start': '2025-04-22', 'end': '2025-06-16'},
    {'country': 'Germany', 'start': '2025-06-16', 'end': '2025-08-07'},
    {'country': 'Turkey', 'start': '2025-08-07', 'end': '2025-09-15'},
    {'country': 'Turkey', 'start': '2025-09-16', 'end': '2025-10-07'},
    {'country': 'Germany', 'start': '2025-10-07', 'end': '2025-11-08'},

    # ========================================
    # FUTURE PLANNED TRAVEL (Optional)
    # ========================================
    # Add planned future trips here if you want to include them in analysis
    # Example:
    # {'country': 'Turkey', 'start': '2025-12-20', 'end': '2026-01-16'},
]

# ============================================================================
# PLANNED TRIPS TO ANALYZE
# ============================================================================

PLANNED_TRIPS = [
    {
        'name': 'December 2025 Trip',
        'start_date': datetime.date(2025, 12, 20),
        'country': 'Turkey',
        'analyze': True  # Set to True to analyze this trip
    },
    # Add more planned trips here as needed
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_travel_history():
    """
    Validate travel history for common errors

    Returns:
        List of validation messages (empty if no issues)
    """
    issues = []

    # Check for gaps or overlaps
    sorted_periods = sorted(TRAVEL_HISTORY, key=lambda x: x['start'])

    for i in range(len(sorted_periods) - 1):
        current = sorted_periods[i]
        next_period = sorted_periods[i + 1]

        current_end = datetime.datetime.strptime(current['end'], '%Y-%m-%d').date()
        next_start = datetime.datetime.strptime(next_period['start'], '%Y-%m-%d').date()

        # Check for gap
        if next_start > current_end + datetime.timedelta(days=1):
            gap_days = (next_start - current_end).days - 1
            issues.append(f"GAP: {gap_days} days between {current['end']} and {next_period['start']}")

        # Check for overlap
        if next_start < current_end:
            issues.append(f"OVERLAP: {current['end']} overlaps with {next_period['start']}")

    return issues


def print_travel_summary():
    """Print a summary of the travel history"""
    print(f"\n{'='*70}")
    print(f"  TRAVEL DATA FOR: {PERSON_NAME}")
    print(f"{'='*70}")
    print(f"Analysis Date: {ANALYSIS_DATE.strftime('%B %d, %Y')}")
    print(f"Buffer Setting: {BUFFER_DAYS} days\n")

    print(f"Total Travel Periods: {len(TRAVEL_HISTORY)}")

    # Count by country
    turkey_periods = [p for p in TRAVEL_HISTORY if p['country'] == 'Turkey']
    germany_periods = [p for p in TRAVEL_HISTORY if p['country'] == 'Germany']

    print(f"  Turkey periods: {len(turkey_periods)}")
    print(f"  Germany periods: {len(germany_periods)}")

    # Calculate total days
    total_turkey_days = 0
    total_germany_days = 0

    for period in TRAVEL_HISTORY:
        start = datetime.datetime.strptime(period['start'], '%Y-%m-%d').date()
        end = datetime.datetime.strptime(period['end'], '%Y-%m-%d').date()
        days = (end - start).days + 1

        if period['country'] == 'Turkey':
            total_turkey_days += days
        else:
            total_germany_days += days

    print(f"\nTotal Days:")
    print(f"  Turkey: {total_turkey_days} days")
    print(f"  Germany: {total_germany_days} days")

    # Validate
    issues = validate_travel_history()
    if issues:
        print(f"\n⚠️  VALIDATION ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print(f"\n✓ Travel history validated - no gaps or overlaps")

    # Planned trips
    active_trips = [t for t in PLANNED_TRIPS if t.get('analyze', False)]
    if active_trips:
        print(f"\nPlanned Trips to Analyze: {len(active_trips)}")
        for trip in active_trips:
            print(f"  - {trip['name']}: {trip['start_date'].strftime('%B %d, %Y')} ({trip['country']})")

    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Run this file directly to see travel summary and validation
    print_travel_summary()
