"""
Turkey-Germany Residence Calculator
Core utility functions for tracking compliance with 183-day rule in rolling 365-day window
"""

import datetime
from datetime import timedelta
from typing import List, Dict, Tuple, Optional
import pandas as pd


class ResidenceCalculator:
    """Calculate and track residence days for Turkey-Germany compliance"""

    TURKEY_LIMIT = 183  # Maximum Turkey days in 365-day rolling window
    WINDOW_DAYS = 365   # Rolling window size

    def __init__(self, periods: List[Dict[str, str]]):
        """
        Initialize calculator with travel history

        Args:
            periods: List of dicts with 'country', 'start', 'end' keys
                    Example: {'country': 'Turkey', 'start': '2025-01-01', 'end': '2025-01-15'}
        """
        self.periods = self._validate_and_sort_periods(periods)

    def _validate_and_sort_periods(self, periods: List[Dict]) -> List[Dict]:
        """Validate periods and sort by start date"""
        validated = []
        for p in periods:
            validated.append({
                'country': p['country'],
                'start': self._parse_date(p['start']),
                'end': self._parse_date(p['end'])
            })
        # Sort by start date
        validated.sort(key=lambda x: x['start'])
        return validated

    def _parse_date(self, date_input) -> datetime.date:
        """Parse date from string or date object"""
        if isinstance(date_input, datetime.date):
            return date_input
        if isinstance(date_input, str):
            return datetime.datetime.strptime(date_input, '%Y-%m-%d').date()
        raise ValueError(f"Invalid date format: {date_input}")

    def calculate_turkey_days_in_window(self, current_date: datetime.date) -> int:
        """
        Calculate Turkey days in the 365-day rolling window ending on current_date

        Args:
            current_date: The end date of the rolling window

        Returns:
            Number of Turkey days in the window
        """
        window_start = current_date - timedelta(days=self.WINDOW_DAYS - 1)
        turkey_days = 0

        for period in self.periods:
            if period['country'] != 'Turkey':
                continue

            # Calculate overlap between period and window
            overlap_start = max(period['start'], window_start)
            overlap_end = min(period['end'], current_date)

            if overlap_start <= overlap_end:
                turkey_days += (overlap_end - overlap_start).days + 1

        return turkey_days

    def get_current_status(self, current_date: datetime.date) -> Dict:
        """
        Get current compliance status

        Args:
            current_date: Date to check status for

        Returns:
            Dict with status information
        """
        turkey_days = self.calculate_turkey_days_in_window(current_date)
        days_remaining = self.TURKEY_LIMIT - turkey_days

        # Find current location
        current_country = 'Germany'  # Default
        for period in self.periods:
            if period['start'] <= current_date <= period['end']:
                current_country = period['country']
                break

        return {
            'date': current_date,
            'current_location': current_country,
            'turkey_days_in_window': turkey_days,
            'days_remaining': days_remaining,
            'compliant': turkey_days <= self.TURKEY_LIMIT,
            'limit': self.TURKEY_LIMIT
        }

    def find_max_trip_duration(
        self,
        trip_start: datetime.date,
        buffer_days: int = 10,
        max_duration: int = 180
    ) -> Dict:
        """
        Find maximum Turkey trip duration while maintaining compliance with buffer

        Args:
            trip_start: Start date of Turkey trip
            buffer_days: Safety buffer (days below limit to maintain)
            max_duration: Maximum trip length to consider (default 180 days)

        Returns:
            Dict with max duration info and analysis
        """
        # Create temporary periods including the potential trip
        best_duration = 0
        results = []

        for duration in range(1, max_duration + 1):
            trip_end = trip_start + timedelta(days=duration - 1)

            # Create scenario with this trip
            test_periods = self.periods.copy()
            test_periods.append({
                'country': 'Turkey',
                'start': trip_start,
                'end': trip_end
            })

            # Create temporary calculator with this scenario
            temp_calc = ResidenceCalculator(test_periods)

            # Check compliance throughout the trip
            max_turkey_days = 0
            violation = False

            current = trip_start
            while current <= trip_end:
                turkey_days = temp_calc.calculate_turkey_days_in_window(current)
                max_turkey_days = max(max_turkey_days, turkey_days)

                if turkey_days > self.TURKEY_LIMIT - buffer_days:
                    violation = True
                    break

                current += timedelta(days=1)

            results.append({
                'duration': duration,
                'trip_end': trip_end,
                'max_turkey_days': max_turkey_days,
                'days_from_limit': self.TURKEY_LIMIT - max_turkey_days,
                'safe': not violation
            })

            if not violation:
                best_duration = duration
            else:
                break  # No point checking longer durations

        if best_duration == 0:
            return {
                'max_duration': 0,
                'recommended_return': trip_start,
                'turkey_days_after_trip': self.calculate_turkey_days_in_window(trip_start),
                'safe': False,
                'message': 'Cannot take trip - already at or above buffer limit'
            }

        best_result = results[best_duration - 1]

        return {
            'max_duration': best_duration,
            'trip_start': trip_start,
            'recommended_return': best_result['trip_end'],
            'max_turkey_days_during_trip': best_result['max_turkey_days'],
            'buffer_maintained': best_result['days_from_limit'],
            'safe': True,
            'all_results': results[:best_duration + 5] if best_duration < max_duration else results
        }

    def simulate_trip(
        self,
        trip_start: datetime.date,
        trip_duration: int
    ) -> Dict:
        """
        Simulate a specific Turkey trip and check compliance

        Args:
            trip_start: Start date of trip
            trip_duration: Duration in days

        Returns:
            Dict with simulation results
        """
        trip_end = trip_start + timedelta(days=trip_duration - 1)

        # Create scenario with this trip
        test_periods = self.periods.copy()
        test_periods.append({
            'country': 'Turkey',
            'start': trip_start,
            'end': trip_end
        })

        temp_calc = ResidenceCalculator(test_periods)

        # Analyze compliance day by day
        daily_data = []
        max_turkey_days = 0
        first_violation = None

        current = trip_start
        while current <= trip_end:
            turkey_days = temp_calc.calculate_turkey_days_in_window(current)
            max_turkey_days = max(max_turkey_days, turkey_days)
            compliant = turkey_days <= self.TURKEY_LIMIT

            daily_data.append({
                'date': current,
                'turkey_days': turkey_days,
                'compliant': compliant
            })

            if not compliant and first_violation is None:
                first_violation = current

            current += timedelta(days=1)

        return {
            'trip_start': trip_start,
            'trip_end': trip_end,
            'trip_duration': trip_duration,
            'max_turkey_days': max_turkey_days,
            'compliant': first_violation is None,
            'first_violation': first_violation,
            'daily_data': daily_data,
            'turkey_days_after_trip': temp_calc.calculate_turkey_days_in_window(trip_end)
        }

    def get_timeline_data(
        self,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> pd.DataFrame:
        """
        Generate daily timeline data for visualization

        Args:
            start_date: Start of timeline
            end_date: End of timeline

        Returns:
            DataFrame with daily status
        """
        dates = pd.date_range(start_date, end_date, freq='D')
        data = []

        for date in dates:
            date_obj = date.date()
            turkey_days = self.calculate_turkey_days_in_window(date_obj)

            # Find country for this date
            country = 'Germany'  # Default
            for period in self.periods:
                if period['start'] <= date_obj <= period['end']:
                    country = period['country']
                    break

            data.append({
                'date': date,
                'country': country,
                'turkey_days_in_window': turkey_days,
                'days_until_limit': self.TURKEY_LIMIT - turkey_days,
                'compliant': turkey_days <= self.TURKEY_LIMIT
            })

        return pd.DataFrame(data)

    def add_period(self, country: str, start: str, end: str):
        """Add a new travel period"""
        new_period = {
            'country': country,
            'start': self._parse_date(start),
            'end': self._parse_date(end)
        }
        self.periods.append(new_period)
        self.periods = self._validate_and_sort_periods(self.periods)

    def get_total_days_by_country(
        self,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None
    ) -> Dict[str, int]:
        """
        Get total days spent in each country

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dict with country names as keys and day counts as values
        """
        totals = {}

        for period in self.periods:
            # Apply date filters if provided
            period_start = period['start']
            period_end = period['end']

            if start_date:
                period_start = max(period_start, start_date)
            if end_date:
                period_end = min(period_end, end_date)

            if period_start <= period_end:
                days = (period_end - period_start).days + 1
                country = period['country']
                totals[country] = totals.get(country, 0) + days

        return totals
