#!/usr/bin/env python3
"""
Turkey Trip Calculator - Check Current Status and Plan Future Trips
Calculates Turkey days in rolling 365-day window and plans safe trips

Usage:
    python check_my_trip.py              # Text output + save visualization
    python check_my_trip.py --show       # Text output + show visualization interactively
    python check_my_trip.py --no-viz     # Text output only (no visualization)
    python check_my_trip.py --quiet      # Minimal output + visualization
"""

import sys
import datetime
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from residence_calculator import ResidenceCalculator

# Import travel data from separate file
# To analyze different people's travel, create a new travel data file and import it instead
from travel_data import TRAVEL_HISTORY, ANALYSIS_DATE, BUFFER_DAYS, PLANNED_TRIPS, PERSON_NAME

# ============================================================================
# CONFIGURATION
# ============================================================================

TODAY = ANALYSIS_DATE  # Current date from travel_data.py

# Get planned trips from travel_data.py
active_planned_trips = [t for t in PLANNED_TRIPS if t.get('analyze', False)]
if active_planned_trips:
    PLANNED_TRIP_START = active_planned_trips[0]['start_date']
else:
    # Default if no planned trips
    PLANNED_TRIP_START = TODAY + timedelta(days=30)


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def print_separator(title="", char="="):
    """Print a formatted separator"""
    if title:
        print(f"\n{char * 70}")
        print(f"  {title}")
        print(f"{char * 70}\n")
    else:
        print(f"{char * 70}\n")


def main():
    """Main analysis function"""

    # Parse command line arguments
    args = sys.argv[1:]
    show_viz = '--show' in args
    no_viz = '--no-viz' in args
    quiet = '--quiet' in args

    # Initialize calculator
    calc = ResidenceCalculator(TRAVEL_HISTORY)

    if not quiet:
        # Fancy header with box drawing
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 12 + "TURKEY-GERMANY RESIDENCE TRACKER" + " " * 24 + "║")
        print("╚" + "═" * 68 + "╝")
        print(f"\n📋 Person: {PERSON_NAME}")
        print(f"📅 Analysis Date: {TODAY.strftime('%B %d, %Y')}")
        print(f"📏 Rule: Maximum 183 Turkey days in any rolling 365-day window")
        print(f"🛡️  Safety Buffer: {BUFFER_DAYS} days")

    # ========================================================================
    # SECTION 1: CURRENT STATUS
    # ========================================================================

    if not quiet:
        print("\n" + "┌" + "─" * 68 + "┐")
        print("│" + " " * 22 + "CURRENT STATUS" + " " * 32 + "│")
        print("└" + "─" * 68 + "┘")

    status = calc.get_current_status(TODAY)

    if not quiet:
        print(f"\n📍 Current Location: {status['current_location']}")
        print(f"🇹🇷 Turkey Days Used: {status['turkey_days_in_window']} / {status['limit']}")
        print(f"⏳ Days Remaining: {status['days_remaining']}")

        # Color-coded status
        if status['compliant']:
            if status['days_remaining'] >= BUFFER_DAYS:
                print(f"✅ Compliance Status: COMPLIANT (Safe)")
            else:
                print(f"⚠️  Compliance Status: COMPLIANT (Below buffer)")
        else:
            print(f"❌ Compliance Status: NON-COMPLIANT")

        if status['days_remaining'] < BUFFER_DAYS and status['compliant']:
            print(f"\n⚠️  WARNING: Only {status['days_remaining']} days from limit!")
            print(f"   Recommended buffer is {BUFFER_DAYS} days.")
    else:
        # Quiet mode - just key info
        print(f"Status: {status['days_remaining']} days remaining ({status['turkey_days_in_window']}/183 used)")

    # ========================================================================
    # SECTION 2: PLANNED TRIP ANALYSIS
    # ========================================================================

    if not quiet:
        print("\n" + "┌" + "─" * 68 + "┐")
        print("│" + " " * 18 + "PLANNED TRIP ANALYSIS" + " " * 29 + "│")
        print("└" + "─" * 68 + "┘")

    if not quiet:
        print(f"\n✈️  Planned Trip Start: {PLANNED_TRIP_START.strftime('%B %d, %Y')}")
        print(f"⏱️  Days Until Trip: {(PLANNED_TRIP_START - TODAY).days} days")
    else:
        print(f"Trip: {PLANNED_TRIP_START.strftime('%b %d, %Y')} ({(PLANNED_TRIP_START - TODAY).days} days away)")

    # Find maximum safe duration
    trip_analysis = calc.find_max_trip_duration(
        trip_start=PLANNED_TRIP_START,
        buffer_days=BUFFER_DAYS,
        max_duration=90  # Check up to 90 days
    )

    if not quiet:
        print(f"\n🎯 Maximum Safe Trip Duration: {trip_analysis['max_duration']} days")

        if trip_analysis['safe']:
            print(f"🏠 Recommended Return Date: {trip_analysis['recommended_return'].strftime('%B %d, %Y')}")
            print(f"📊 Max Turkey Days During Trip: {trip_analysis['max_turkey_days_during_trip']} / {status['limit']}")
            print(f"🛡️  Buffer After Trip: {trip_analysis['buffer_maintained']} days")

            # Calculate status on return date
            calc_with_trip = ResidenceCalculator(TRAVEL_HISTORY + [{
                'country': 'Turkey',
                'start': PLANNED_TRIP_START.strftime('%Y-%m-%d'),
                'end': trip_analysis['recommended_return'].strftime('%Y-%m-%d')
            }])
            return_status = calc_with_trip.get_current_status(trip_analysis['recommended_return'])

            print(f"\n📈 Status After Trip (on return date):")
            print(f"   Turkey Days in Window: {return_status['turkey_days_in_window']} / {status['limit']}")
            print(f"   Days Remaining: {return_status['days_remaining']}")
        else:
            print("\n⚠️  WARNING: Cannot safely take trip with current buffer settings")
            print(f"   {trip_analysis['message']}")
    else:
        # Quiet mode - concise output
        if trip_analysis['safe']:
            print(f"Max duration: {trip_analysis['max_duration']} days (return {trip_analysis['recommended_return'].strftime('%b %d, %Y')})")
            print(f"After trip: {trip_analysis['buffer_maintained']} days buffer remaining")
        else:
            print(f"WARNING: Trip not safe - {trip_analysis['message']}")

    # ========================================================================
    # SECTION 3: ALTERNATIVE SCENARIOS (skip in quiet mode)
    # ========================================================================

    if not quiet:
        print("\n" + "┌" + "─" * 68 + "┐")
        print("│" + " " * 18 + "ALTERNATIVE TRIP DURATIONS" + " " * 24 + "│")
        print("└" + "─" * 68 + "┘")

        print("\nTesting different trip lengths:\n")
        print(f"{'Duration':<12} {'Return Date':<15} {'Turkey Days':<15} {'Buffer':<10} {'Safe?':<10}")
        print("-" * 70)

        test_durations = [14, 21, 28, 35, 42, 49, 56]

        for duration in test_durations:
            return_date = PLANNED_TRIP_START + timedelta(days=duration - 1)

            # Simulate this trip
            simulation = calc.simulate_trip(PLANNED_TRIP_START, duration)

            buffer = 183 - simulation['max_turkey_days']
            safe_status = "✓ YES" if simulation['compliant'] and buffer >= BUFFER_DAYS else "✗ NO"

            print(f"{duration} days     {return_date.strftime('%b %d, %Y'):<15} "
                  f"{simulation['max_turkey_days']:<15} {buffer:<10} {safe_status:<10}")

    # ========================================================================
    # SECTION 4: YEAR OVERVIEW (skip in quiet mode)
    # ========================================================================

    if not quiet:
        print("\n" + "┌" + "─" * 68 + "┐")
        print("│" + " " * 22 + "TRAVEL SUMMARY" + " " * 32 + "│")
        print("└" + "─" * 68 + "┘")

        # 2025 totals
        totals_2025 = calc.get_total_days_by_country(
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 12, 31)
        )

        print("\n📊 2025 Travel Days (so far):")
        print(f"   🇹🇷 Turkey:  {totals_2025.get('Turkey', 0)} days")
        print(f"   🇩🇪 Germany: {totals_2025.get('Germany', 0)} days")

        # If taking the recommended trip
        if trip_analysis['safe']:
            trip_days = trip_analysis['max_duration']
            print(f"\n📊 2025 Travel Days (including recommended trip):")
            print(f"   🇹🇷 Turkey:  {totals_2025.get('Turkey', 0) + trip_days} days")
            print(f"   🇩🇪 Germany: {totals_2025.get('Germany', 0)} days")

    # ========================================================================
    # SECTION 5: VISUALIZATIONS
    # ========================================================================

    if not no_viz:
        if not quiet:
            print("\n" + "┌" + "─" * 68 + "┐")
            print("│" + " " * 20 + "GENERATING VISUALIZATION" + " " * 24 + "│")
            print("└" + "─" * 68 + "┘\n")

        create_visualizations(calc, TODAY, PLANNED_TRIP_START, trip_analysis, show=show_viz)

        if not quiet:
            print("✅ Visualization saved as 'residence_analysis.png'")

    if not quiet:
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 23 + "ANALYSIS COMPLETE" + " " * 28 + "║")
        print("╚" + "═" * 68 + "╝\n")


def create_visualizations(calc, today, trip_start, trip_analysis, show=False):
    """
    Create visualization chart - single combined plot with labeled inflection points

    Args:
        calc: ResidenceCalculator instance
        today: Current date
        trip_start: Trip start date
        trip_analysis: Trip analysis results dict
        show: If True, display plot interactively. Otherwise just save to file.
    """

    # Prepare data including the planned trip and future Germany stay
    future_periods = []

    if trip_analysis['safe']:
        # Add the recommended Turkey trip
        future_periods.append({
            'country': 'Turkey',
            'start': trip_start.strftime('%Y-%m-%d'),
            'end': trip_analysis['recommended_return'].strftime('%Y-%m-%d')
        })

        # Add Germany period after return until end of March 2026
        germany_return = trip_analysis['recommended_return'] + timedelta(days=1)
        future_periods.append({
            'country': 'Germany',
            'start': germany_return.strftime('%Y-%m-%d'),
            'end': '2026-03-31'
        })

        timeline_end = datetime.date(2026, 3, 31)
    else:
        # If trip not safe, just show Germany until March
        future_periods.append({
            'country': 'Germany',
            'start': today.strftime('%Y-%m-%d'),
            'end': '2026-03-31'
        })
        timeline_end = datetime.date(2026, 3, 31)

    # Create calculator with future periods
    calc_with_future = ResidenceCalculator(TRAVEL_HISTORY + future_periods)

    # Get timeline data
    timeline_start = datetime.date(2024, 9, 15)
    df = calc_with_future.get_timeline_data(timeline_start, timeline_end)

    # Find inflection points (local maxima/minima and important dates)
    inflection_points = []

    # Add today
    today_data = df[df['date'] == pd.Timestamp(today)]
    if not today_data.empty:
        days_remaining = 183 - today_data.iloc[0]['turkey_days_in_window']
        inflection_points.append({
            'date': today,
            'value': days_remaining,
            'label': f"Today ({today.strftime('%b %d')})\n{days_remaining:.0f} days left"
        })

    # Add trip start
    if trip_analysis['safe']:
        trip_start_data = df[df['date'] == pd.Timestamp(trip_start)]
        if not trip_start_data.empty:
            days_remaining = 183 - trip_start_data.iloc[0]['turkey_days_in_window']
            inflection_points.append({
                'date': trip_start,
                'value': days_remaining,
                'label': f"Trip Start\n{trip_start.strftime('%b %d, %Y')}\n{days_remaining:.0f} days left"
            })

        # Add return date
        return_data = df[df['date'] == pd.Timestamp(trip_analysis['recommended_return'])]
        if not return_data.empty:
            days_remaining = 183 - return_data.iloc[0]['turkey_days_in_window']
            inflection_points.append({
                'date': trip_analysis['recommended_return'],
                'value': days_remaining,
                'label': f"Return\n{trip_analysis['recommended_return'].strftime('%b %d, %Y')}\n{days_remaining:.0f} days left"
            })

    # Add end of timeline
    end_data = df[df['date'] == pd.Timestamp(timeline_end)]
    if not end_data.empty:
        days_remaining = 183 - end_data.iloc[0]['turkey_days_in_window']
        inflection_points.append({
            'date': timeline_end,
            'value': days_remaining,
            'label': f"End of Timeline\n{timeline_end.strftime('%b %d, %Y')}\n{days_remaining:.0f} days left"
        })

    # Find local maxima/minima in the data
    turkey_days_series = df['turkey_days_in_window'].values
    for i in range(1, len(turkey_days_series) - 1):
        # Local maximum
        if turkey_days_series[i] > turkey_days_series[i-1] and turkey_days_series[i] > turkey_days_series[i+1]:
            if abs(turkey_days_series[i] - turkey_days_series[i-1]) > 5:  # Significant change
                date_val = df.iloc[i]['date'].date()
                # Don't add if too close to existing points
                if all(abs((date_val - p['date']).days) > 20 for p in inflection_points):
                    inflection_points.append({
                        'date': date_val,
                        'value': turkey_days_series[i],
                        'label': f"{turkey_days_series[i]:.0f}"
                    })

    # Create single plot
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    fig.suptitle(f'Turkey Days Available in Rolling 365-Day Window - {PERSON_NAME}',
                 fontsize=16, fontweight='bold')

    # Background coloring for countries
    turkey_mask = df['country'] == 'Turkey'
    germany_mask = df['country'] == 'Germany'

    # Fill background based on location
    ax.fill_between(df['date'], 0, 200, where=turkey_mask,
                    color='#e74c3c', alpha=0.15, label='In Turkey', step='post')
    ax.fill_between(df['date'], 0, 200, where=germany_mask,
                    color='#3498db', alpha=0.15, label='In Germany', step='post')

    # Split data into past and future for different line styles
    past_mask = df['date'] <= pd.Timestamp(today)
    future_mask = df['date'] > pd.Timestamp(today)

    # Calculate days remaining (183 - days spent)
    df['days_available'] = 183 - df['turkey_days_in_window']

    # Plot main line - past (solid)
    ax.plot(df.loc[past_mask, 'date'],
            df.loc[past_mask, 'days_available'],
            linewidth=3, color='#27ae60', label='Historical', zorder=5)

    # Plot main line - future (dashed)
    if future_mask.any():
        ax.plot(df.loc[future_mask, 'date'],
                df.loc[future_mask, 'days_available'],
                linewidth=3, color='#2ecc71', linestyle='--',
                label='Projected', zorder=5)

    # Add reference lines
    ax.axhline(y=0, color='red', linestyle='-', linewidth=2.5,
               label='Limit Reached (0 days left)', zorder=3)
    ax.axhline(y=BUFFER_DAYS, color='orange', linestyle='--',
               linewidth=2, label=f'Minimum Buffer ({BUFFER_DAYS} days)',
               alpha=0.8, zorder=3)

    # Mark today with vertical line
    ax.axvline(x=pd.Timestamp(today), color='blue', linestyle='-',
               linewidth=2, label='Today', alpha=0.7, zorder=4)

    # Add inflection point labels
    for point in inflection_points:
        ax.plot(pd.Timestamp(point['date']), point['value'],
                'o', markersize=8, color='darkgreen', zorder=10)

        # Position label above or below based on value
        y_offset = 10 if point['value'] > 30 else -25
        ax.annotate(point['label'],
                   xy=(pd.Timestamp(point['date']), point['value']),
                   xytext=(0, y_offset), textcoords='offset points',
                   ha='center', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow',
                            alpha=0.7, edgecolor='black', linewidth=1),
                   zorder=11)

    # Styling
    ax.set_ylabel('Days Available to Spend in Turkey', fontweight='bold', fontsize=12)
    ax.set_xlabel('Date', fontweight='bold', fontsize=12)
    ax.set_ylim(-20, 200)
    ax.grid(True, alpha=0.3, zorder=0)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig('residence_analysis.png', dpi=150, bbox_inches='tight')

    if show:
        plt.show()  # Display interactively
    else:
        plt.close()  # Just save and close


if __name__ == "__main__":
    main()
