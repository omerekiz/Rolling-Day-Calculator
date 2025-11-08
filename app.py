"""
Turkey-Germany Residence Tracker - Streamlit Web App
Interactive interface for tracking and planning Turkey residency compliance
"""

import streamlit as st
import datetime
from datetime import timedelta
import pandas as pd
import altair as alt
from residence_calculator import ResidenceCalculator
from config import DataManager

# Page config
st.set_page_config(
    page_title="Turkey-Germany Residence Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

dm = get_data_manager()

# Session state initialization
if 'person_id' not in st.session_state:
    people = dm.get_available_people()
    st.session_state.person_id = people[0] if people else 'omer'

if 'data' not in st.session_state:
    st.session_state.data = dm.load_person_data(st.session_state.person_id)

if 'unsaved_changes' not in st.session_state:
    st.session_state.unsaved_changes = False

if 'planned_trips' not in st.session_state:
    st.session_state.planned_trips = []

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("⚙️ Settings")

    # Person selector
    people = dm.get_available_people()
    selected_person = st.selectbox(
        "Select Person",
        people,
        index=people.index(st.session_state.person_id) if st.session_state.person_id in people else 0
    )

    if selected_person != st.session_state.person_id:
        st.session_state.person_id = selected_person
        st.session_state.data = dm.load_person_data(selected_person)
        st.session_state.unsaved_changes = False
        st.session_state.planned_trips = []
        st.rerun()

    st.divider()

    # Buffer days
    buffer_days = st.slider(
        "Safety Buffer (days)",
        min_value=0,
        max_value=30,
        value=st.session_state.data['buffer_days'],
        help="Stay this many days below the 183-day limit"
    )

    if buffer_days != st.session_state.data['buffer_days']:
        st.session_state.data['buffer_days'] = buffer_days
        st.session_state.unsaved_changes = True

    st.divider()

    # Auto-save when buffer changes
    if st.session_state.unsaved_changes:
        dm.save_person_data(st.session_state.person_id, st.session_state.data)
        st.session_state.unsaved_changes = False
        st.success("✅ Buffer setting saved", icon="💾")

# ============================================================================
# MAIN AREA
# ============================================================================

st.title(f"✈️ Turkey-Germany Residence Tracker")
st.caption(f"Tracking compliance for **{st.session_state.data['person_name']}**")

# Always use today's date
today = datetime.date.today()

# Create calculator
calc = ResidenceCalculator(st.session_state.data['travel_history'])
status = calc.get_current_status(today)

# ============================================================================
# TABS
# ============================================================================

tab1, tab2 = st.tabs(["🎯 Trip Planner", "📝 Travel History"])

# ============================================================================
# TAB 1: TRIP PLANNER
# ============================================================================

with tab1:
    # Current Status
    st.header("📊 Current Status")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Location", status['current_location'])

    with col2:
        st.metric("Turkey Days Used", f"{status['turkey_days_in_window']}/183")

    with col3:
        days_color = "normal" if status['days_remaining'] >= buffer_days else "inverse"
        st.metric(
            "Days Remaining",
            status['days_remaining'],
            delta=f"{status['days_remaining'] - buffer_days} above buffer" if status['days_remaining'] > buffer_days else f"{buffer_days - status['days_remaining']} below buffer",
            delta_color=days_color
        )

    with col4:
        if status['compliant']:
            if status['days_remaining'] >= buffer_days:
                st.success("✅ COMPLIANT\n(Safe)")
            else:
                st.warning("⚠️ COMPLIANT\n(Below buffer)")
        else:
            st.error("❌ NON-COMPLIANT")

    st.divider()

    # Trip Planning
    st.header("✈️ Plan Your Trips")

    # Add trip button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("➕ Add Trip"):
            st.session_state.planned_trips.append({
                'id': len(st.session_state.planned_trips),
                'name': f"Trip {len(st.session_state.planned_trips) + 1}",
                'start_date': today + timedelta(days=7),
                'end_date': today + timedelta(days=14),
                'country': 'Turkey'
            })
            st.rerun()

    # Display and edit trips
    if st.session_state.planned_trips:
        for idx, trip in enumerate(st.session_state.planned_trips):
            with st.expander(f"**{trip['name']}**", expanded=True):
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                with col1:
                    new_start = st.date_input(
                        "Start Date",
                        value=trip['start_date'],
                        min_value=today,
                        key=f"start_{idx}"
                    )
                    if new_start != trip['start_date']:
                        st.session_state.planned_trips[idx]['start_date'] = new_start
                        # Adjust end date if it's now before start date
                        if trip['end_date'] < new_start:
                            st.session_state.planned_trips[idx]['end_date'] = new_start + timedelta(days=7)

                with col2:
                    # Read current values from session state (source of truth)
                    current_start_date = st.session_state.planned_trips[idx]['start_date']
                    current_end_date = st.session_state.planned_trips[idx]['end_date']

                    # Ensure end_date is not before start_date
                    safe_end_date = max(current_end_date, current_start_date)

                    # If we had to adjust, update session state
                    if safe_end_date != current_end_date:
                        st.session_state.planned_trips[idx]['end_date'] = safe_end_date
                        current_end_date = safe_end_date

                    new_end = st.date_input(
                        "End Date",
                        value=current_end_date,
                        min_value=current_start_date,
                        key=f"end_{idx}"
                    )

                    # Update session state if widget changed
                    if new_end != current_end_date:
                        st.session_state.planned_trips[idx]['end_date'] = new_end
                        current_end_date = new_end
                    else:
                        print(f"End date not changed: {current_end_date}")

                with col3:
                    # Calculate duration using session state values
                    actual_end = st.session_state.planned_trips[idx]['end_date']
                    actual_start = st.session_state.planned_trips[idx]['start_date']
                    duration = (actual_end - actual_start).days + 1
                    st.metric("Duration", f"{duration} days")

                    # Display any stored messages from previous max days calculation
                    if 'max_days_message' in st.session_state:
                        msg_type, msg = st.session_state.max_days_message
                        if msg_type == 'success':
                            st.success(msg)
                        elif msg_type == 'error':
                            st.error(msg)
                        del st.session_state.max_days_message

                    # Use Max Days button
                    if st.button("Use Max Days", key=f"max_{idx}"):
                        # Use session state values (source of truth)
                        trip_start_date = st.session_state.planned_trips[idx]['start_date']
                        print("\n" + "="*80)
                        print(f"USE MAX DAYS CLICKED - Trip {idx}")
                        print(f"Start date: {trip_start_date}")
                        print(f"Buffer days: {buffer_days}")
                        print(f"Current end date: {current_end_date}")
                        print("="*80)

                        # Calculate maximum trip duration
                        trip_analysis = calc.find_max_trip_duration(
                            trip_start=trip_start_date,
                            buffer_days=buffer_days,
                            max_duration=365  # Allow trips up to a year
                        )

                        recommended_return = trip_analysis.get('recommended_return')

                        print(f"\nRESULT:")
                        print(f"  safe: {trip_analysis.get('safe')}")
                        print(f"  max_duration: {trip_analysis.get('max_duration')}")
                        print(f"  recommended_return: {recommended_return}")
                        print(f"  buffer_maintained: {trip_analysis.get('buffer_maintained')}")
                        print(f"  Full response: {trip_analysis}")
                        print("="*80 + "\n")

                        if trip_analysis.get('safe') and trip_analysis.get('max_duration', 0) > 0 and recommended_return:
                            # Update the end date - store in session state (source of truth)
                            print(f"✅ UPDATING end_date from {st.session_state.planned_trips[idx]['end_date']} to {recommended_return}")
                            st.session_state.planned_trips[idx]['end_date'] = recommended_return
                            # Store success message for display after rerun
                            st.session_state.max_days_message = ('success', f"✅ Updated! Max trip: {trip_analysis['max_duration']} days (return {recommended_return.strftime('%b %d, %Y')}), Buffer: {trip_analysis['buffer_maintained']} days")
                            st.rerun()
                        else:
                            msg = trip_analysis.get('message', 'Cannot calculate - already at or above buffer limit')
                            print(f"❌ FAILED: {msg}")
                            st.session_state.max_days_message = ('error', f"⚠️ {msg}")
                            st.error(f"⚠️ {msg}")
                            st.write("Debug info:", trip_analysis)

                with col4:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.planned_trips.pop(idx)
                        st.rerun()

                # Validation - use session state values (source of truth)
                validation_start = st.session_state.planned_trips[idx]['start_date']
                validation_end = st.session_state.planned_trips[idx]['end_date']
                test_trip = {
                    'country': 'Turkey',
                    'start': validation_start.strftime('%Y-%m-%d'),
                    'end': validation_end.strftime('%Y-%m-%d')
                }
                calc_with_trip = ResidenceCalculator(st.session_state.data['travel_history'] + [test_trip])
                trip_status = calc_with_trip.get_current_status(validation_end)

                if not trip_status['compliant']:
                    st.error(f"❌ This trip exceeds the 183-day limit! ({183 - trip_status['days_remaining']} days over)")
                elif trip_status['days_remaining'] < buffer_days:
                    st.warning(f"⚠️ Below buffer: Only {trip_status['days_remaining']} days remaining (buffer: {buffer_days})")
                else:
                    st.success(f"✅ Safe trip: {trip_status['days_remaining']} days remaining after return")
    else:
        st.info("No trips planned. Click 'Add Trip' to start planning.")

    st.divider()

    # Visualization
    st.header("📈 Compliance Timeline")

    # Prepare data for visualization
    future_periods = []
    for trip in st.session_state.planned_trips:
        future_periods.append({
            'country': trip['country'],
            'start': trip['start_date'].strftime('%Y-%m-%d'),
            'end': trip['end_date'].strftime('%Y-%m-%d')
        })

    # Fill gaps with Germany
    all_periods = st.session_state.data['travel_history'] + future_periods
    calc_with_future = ResidenceCalculator(all_periods)

    # Get timeline data
    timeline_start = datetime.date(2024, 9, 15)
    timeline_end = max(datetime.date(2026, 3, 31),
                       max([trip['end_date'] for trip in st.session_state.planned_trips] + [today]))

    df = calc_with_future.get_timeline_data(timeline_start, timeline_end)
    df['days_available'] = 183 - df['turkey_days_in_window']
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

    # Find inflection points for labeling
    inflection_data = []

    # Add today
    today_idx = df[df['date'] == pd.Timestamp(today)].index
    if len(today_idx) > 0:
        idx = today_idx[0]
        inflection_data.append({
            'date': df.iloc[idx]['date'],
            'days_available': df.iloc[idx]['days_available'],
            'label': f"Today\n{df.iloc[idx]['days_available']:.0f} days"
        })

    # Add trip start/end dates
    for trip in st.session_state.planned_trips:
        trip_start_idx = df[df['date'] == pd.Timestamp(trip['start_date'])].index
        if len(trip_start_idx) > 0:
            idx = trip_start_idx[0]
            inflection_data.append({
                'date': df.iloc[idx]['date'],
                'days_available': df.iloc[idx]['days_available'],
                'label': f"Start\n{df.iloc[idx]['days_available']:.0f} days"
            })

        trip_end_idx = df[df['date'] == pd.Timestamp(trip['end_date'])].index
        if len(trip_end_idx) > 0:
            idx = trip_end_idx[0]
            inflection_data.append({
                'date': df.iloc[idx]['date'],
                'days_available': df.iloc[idx]['days_available'],
                'label': f"Return\n{df.iloc[idx]['days_available']:.0f} days"
            })

    # Create Altair chart
    base = alt.Chart(df).encode(
        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %d', labelAngle=-45))
    )

    # Line chart for days available
    line = base.mark_line(size=3, color='#27ae60').encode(
        y=alt.Y('days_available:Q', title='Days Available to Spend in Turkey', scale=alt.Scale(domain=[-20, 200])),
        tooltip=[
            alt.Tooltip('date:T', title='Date', format='%b %d, %Y'),
            alt.Tooltip('days_available:Q', title='Days Available'),
            alt.Tooltip('turkey_days_in_window:Q', title='Turkey Days Used'),
            alt.Tooltip('country:N', title='Location')
        ]
    )

    # Reference lines
    buffer_line = alt.Chart(pd.DataFrame({'y': [buffer_days]})).mark_rule(
        strokeDash=[5, 5],
        color='orange',
        size=2
    ).encode(y='y:Q')

    limit_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='red',
        size=2
    ).encode(y='y:Q')

    # Today marker
    today_line = alt.Chart(pd.DataFrame({'x': [pd.Timestamp(today)]})).mark_rule(
        color='blue',
        size=2
    ).encode(x='x:T')

    # Add inflection point markers with tooltips
    inflection_points = None
    if inflection_data:
        inflection_df = pd.DataFrame(inflection_data)

        # Points with tooltips
        inflection_points = alt.Chart(inflection_df).mark_circle(
            size=100,
            color='darkgreen',
            opacity=0.8
        ).encode(
            x='date:T',
            y='days_available:Q',
            tooltip=[
                alt.Tooltip('date:T', title='Date', format='%b %d, %Y'),
                alt.Tooltip('days_available:Q', title='Days Available', format='.0f'),
                alt.Tooltip('label:N', title='Event')
            ]
        )

    # Combine
    if inflection_points is not None:
        chart = (line + buffer_line + limit_line + today_line + inflection_points).properties(
            height=400,
            title='Days Available Over Time'
        ).interactive()
    else:
        chart = (line + buffer_line + limit_line + today_line).properties(
            height=400,
            title='Days Available Over Time'
        ).interactive()

    st.altair_chart(chart, width='stretch')

    st.divider()

    # Generate Report
    st.header("📋 Generate Report")

    if st.button("📄 Generate Trip Report"):
        st.subheader("Trip Planning Report")
        st.write(f"**Generated:** {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}")
        st.write(f"**Person:** {st.session_state.data['person_name']}")
        st.write(f"**Buffer Setting:** {buffer_days} days")

        st.divider()

        st.write("**Current Status:**")
        st.write(f"- Location: {status['current_location']}")
        st.write(f"- Turkey days used: {status['turkey_days_in_window']} / 183")
        st.write(f"- Days remaining: {status['days_remaining']}")
        st.write(f"- Compliance: {'✅ COMPLIANT' if status['compliant'] else '❌ NON-COMPLIANT'}")

        if st.session_state.planned_trips:
            st.divider()
            st.write("**Planned Trips:**")
            for trip in st.session_state.planned_trips:
                duration = (trip['end_date'] - trip['start_date']).days + 1
                st.write(f"\n**{trip['name']}**")
                st.write(f"- Dates: {trip['start_date'].strftime('%B %d, %Y')} → {trip['end_date'].strftime('%B %d, %Y')}")
                st.write(f"- Duration: {duration} days")

                # Check compliance
                test_trip = {
                    'country': 'Turkey',
                    'start': trip['start_date'].strftime('%Y-%m-%d'),
                    'end': trip['end_date'].strftime('%Y-%m-%d')
                }
                calc_test = ResidenceCalculator(st.session_state.data['travel_history'] + [test_trip])
                test_status = calc_test.get_current_status(trip['end_date'])

                if test_status['compliant']:
                    if test_status['days_remaining'] >= buffer_days:
                        st.write(f"- Status: ✅ Safe ({test_status['days_remaining']} days remaining)")
                    else:
                        st.write(f"- Status: ⚠️ Below buffer ({test_status['days_remaining']} days remaining)")
                else:
                    st.write(f"- Status: ❌ Non-compliant ({-test_status['days_remaining']} days over limit)")

# ============================================================================
# TAB 2: TRAVEL HISTORY
# ============================================================================

with tab2:
    st.header("📝 Travel History")
    st.caption("Edit your past travel periods. Changes will be saved when you click Save in the sidebar.")

    # Display as editable dataframe
    travel_df = pd.DataFrame(st.session_state.data['travel_history'])

    if not travel_df.empty:
        # Convert string dates to datetime for proper editing
        travel_df['start'] = pd.to_datetime(travel_df['start'])
        travel_df['end'] = pd.to_datetime(travel_df['end'])

        # Show data
        edited_df = st.data_editor(
            travel_df,
            width='stretch',
            num_rows="dynamic",
            column_config={
                "country": st.column_config.SelectboxColumn(
                    "Country",
                    options=["Turkey", "Germany"],
                    required=True
                ),
                "start": st.column_config.DateColumn(
                    "Start Date",
                    format="YYYY-MM-DD",
                    required=True
                ),
                "end": st.column_config.DateColumn(
                    "End Date",
                    format="YYYY-MM-DD",
                    required=True
                )
            },
            hide_index=True
        )

        # Check if data changed
        if not edited_df.equals(travel_df):
            # Convert dates back to strings for storage
            edited_copy = edited_df.copy()
            edited_copy['start'] = edited_copy['start'].dt.strftime('%Y-%m-%d')
            edited_copy['end'] = edited_copy['end'].dt.strftime('%Y-%m-%d')
            st.session_state.data['travel_history'] = edited_copy.to_dict('records')
            st.session_state.unsaved_changes = True
            st.rerun()
    else:
        st.info("No travel history yet. Add a row below to start tracking.")

        # Show empty editor with proper types
        empty_df = pd.DataFrame(columns=["country", "start", "end"])
        empty_df['start'] = pd.to_datetime(empty_df['start'])
        empty_df['end'] = pd.to_datetime(empty_df['end'])

        edited_df = st.data_editor(
            empty_df,
            width='stretch',
            num_rows="dynamic",
            column_config={
                "country": st.column_config.SelectboxColumn(
                    "Country",
                    options=["Turkey", "Germany"],
                    required=True
                ),
                "start": st.column_config.DateColumn(
                    "Start Date",
                    format="YYYY-MM-DD",
                    required=True
                ),
                "end": st.column_config.DateColumn(
                    "End Date",
                    format="YYYY-MM-DD",
                    required=True
                )
            },
            hide_index=True
        )

        if not edited_df.empty:
            # Convert dates to strings for storage
            edited_copy = edited_df.copy()
            edited_copy['start'] = edited_copy['start'].dt.strftime('%Y-%m-%d')
            edited_copy['end'] = edited_copy['end'].dt.strftime('%Y-%m-%d')
            st.session_state.data['travel_history'] = edited_copy.to_dict('records')
            st.session_state.unsaved_changes = True
            st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("💡 Tip: Plan your trips in the Trip Planner tab. Only your buffer setting and travel history are saved to disk.")
