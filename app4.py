import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import json
import os
from typing import Dict, List, Optional
import uuid


st.set_page_config(
    page_title="MediTracker Pro",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class MedicationTracker:
    def __init__(self):
        self.data_file = "medication_data.json"
        self.load_data()
    
    def load_data(self):
        """Load existing data or initialize empty structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.medications = data.get('medications', {})
                    self.logs = data.get('logs', [])
                    self.mood_logs = data.get('mood_logs', [])
                    self.side_effects = data.get('side_effects', [])
            except:
                self.initialize_empty_data()
        else:
            self.initialize_empty_data()
    
    def initialize_empty_data(self):
        """Initialize empty data structure"""
        self.medications = {}
        self.logs = []
        self.mood_logs = []
        self.side_effects = []
    
    def save_data(self):
        """Save data to JSON file"""
        data = {
            'medications': self.medications,
            'logs': self.logs,
            'mood_logs': self.mood_logs,
            'side_effects': self.side_effects
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_medication(self, name: str, dosage: str, frequency: str, times: List[str], notes: str = ""):
        """Add a new medication"""
        med_id = str(uuid.uuid4())
        self.medications[med_id] = {
            'name': name,
            'dosage': dosage,
            'frequency': frequency,
            'times': times,
            'notes': notes,
            'created_date': datetime.now().isoformat(),
            'active': True
        }
        self.save_data()
        return med_id
    
    def log_side_effect(self, med_id: str, effect: str, severity: int, notes: str = ""):
        """Log side effect"""
        side_effect_entry = {
            'id': str(uuid.uuid4()),
            'med_id': med_id,
            'timestamp': datetime.now().isoformat(),
            'effect': effect,
            'severity': severity,
            'notes': notes
        }
        self.side_effects.append(side_effect_entry)
        self.save_data()
    
    def log_mood(self, mood_score: int, notes: str = ""):
        """Log mood entry"""
        mood_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'mood_score': mood_score,
            'notes': notes
        }
        self.mood_logs.append(mood_entry)
        self.save_data()
    
    def delete_medication(self, med_id: str):
        """Delete/remove a medication completely"""
        if med_id in self.medications:
            del self.medications[med_id]
            self.save_data()
            return True
        return False
    
    def archive_medication(self, med_id: str, reason: str = ""):
        """Archive a medication (mark as inactive but keep history)"""
        if med_id in self.medications:
            self.medications[med_id]['active'] = False
            self.medications[med_id]['archived_date'] = datetime.now().isoformat()
            self.medications[med_id]['archive_reason'] = reason
            self.save_data()
            return True
        return False
    
    def reactivate_medication(self, med_id: str):
        """Reactivate an archived medication"""
        if med_id in self.medications:
            self.medications[med_id]['active'] = True
            if 'archived_date' in self.medications[med_id]:
                del self.medications[med_id]['archived_date']
            if 'archive_reason' in self.medications[med_id]:
                del self.medications[med_id]['archive_reason']
            self.save_data()
            return True
        return False
    

if 'tracker' not in st.session_state:
    st.session_state.tracker = MedicationTracker()

tracker = st.session_state.tracker

st.markdown('<h1 class="main-header">💊 MediTracker Pro</h1>', unsafe_allow_html=True)


st.sidebar.title("Navigation")


if 'quick_action' in st.session_state:
    if st.session_state.quick_action == "side_effect":
        default_page = "Side Effects"
    else:
        default_page = "Dashboard"
  
    del st.session_state.quick_action
else:
    default_page = "Dashboard"


page_options = [
    "Dashboard", 
    "Add Medication", 
    "Manage Medications",
    "Side Effects"
]

try:
    default_index = page_options.index(default_page)
except ValueError:
    default_index = 0

page = st.sidebar.selectbox("Choose a page:", page_options, index=default_index)


if page == "Dashboard":
    st.header("📊 Dashboard")
    
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Medications", len([m for m in tracker.medications.values() if m['active']]))
    
    with col2:
        recent_side_effects = len([se for se in tracker.side_effects if 
                                 datetime.fromisoformat(se['timestamp']) >= datetime.now() - timedelta(days=7)])
        st.metric("Side Effects (7d)", recent_side_effects)
    
    with col3:
        archived_count = len([m for m in tracker.medications.values() if not m['active']])
        st.metric("Archived Meds", archived_count)
    

    st.subheader("💊 Active Medications")
    
    active_meds = {med_id: med for med_id, med in tracker.medications.items() if med['active']}
    
    if active_meds:
        for med_id, med in list(active_meds.items())[:5]:  # Show first 5
            st.write(f"**{med['name']}** ({med['dosage']}) - {med['frequency']}")
            st.caption(f"Schedule: {', '.join(med['times'])}")
        
        if len(active_meds) > 5:
            st.info(f"... and {len(active_meds) - 5} more medications. View all in Manage Medications.")
    else:
        st.info("No medications scheduled. Add a medication to get started.")
    

    st.subheader("⚡ Quick Actions")
    
    if st.button("⚠️ Report Side Effect", use_container_width=True):
        st.session_state.quick_action = "side_effect"
        st.rerun()


elif page == "Add Medication":
    st.header("💊 Add New Medication")
    
    with st.form("add_medication"):
        col1, col2 = st.columns(2)
        
        with col1:
            med_name = st.text_input("Medication Name*", placeholder="e.g., Aspirin")
            dosage = st.text_input("Dosage*", placeholder="e.g., 100mg")
            
           
            doses_per_day = st.number_input(
                "How many times per day?", 
                min_value=1, 
                max_value=8, 
                value=1,
                help="Enter the total number of times you need to take this medication each day"
            )
        
        with col2:
            st.write("**🕐 Medication Times**")
            
           
            times = []
            
            if doses_per_day >= 1:
                st.write(f"**Set times for your {doses_per_day} daily dose(s):**")
                
                
                all_times_set = True
                for i in range(doses_per_day):
                    dose_time = st.time_input(
                        f"Dose {i+1} time", 
                        value=None,
                        key=f"dose_time_{i}",
                        help=f"Please select the time for dose {i+1}"
                    )
                    
                    
                    if dose_time is not None:
                        times.append(dose_time.strftime("%H:%M"))
                    else:
                        all_times_set = False

                
                if len(times) == doses_per_day and all_times_set:
                    st.success(f"✅ **Daily Schedule:** {', '.join(times)}")
                    st.caption(f"📅 {doses_per_day} doses per day at your chosen times")
                elif not all_times_set:
                    st.warning("⚠️ Please select times for all doses")

        
        notes = st.text_area("Notes (optional)", placeholder="Special instructions, warnings, etc.")
        
        submitted = st.form_submit_button("Add Medication", use_container_width=True)
        
        if submitted:
            
            if med_name and dosage and len(times) == doses_per_day and all(times):
                
                times.sort()
                
                
                frequency_label = f"{doses_per_day} times daily"
                
                med_id = tracker.add_medication(med_name, dosage, frequency_label, times, notes)
                
                st.success(f"✅ **Successfully added {med_name}!**")
                st.success(f"📅 **Schedule:** {len(times)} doses daily at {', '.join(times)}")
                
                st.balloons()
                st.rerun()
            else:
                error_messages = []
                if not med_name:
                    error_messages.append("medication name")
                if not dosage:
                    error_messages.append("dosage")
                if len(times) != doses_per_day or not all(times):
                    error_messages.append("all medication times")
                
                st.error(f"❌ Please fill in: {', '.join(error_messages)}")


elif page == "Manage Medications":
    st.header("⚙️ Manage Medications")
    
    
    tab1, tab2, tab3 = st.tabs(["Active Medications", "Archived Medications", "Bulk Actions"])
    
    with tab1:
        st.subheader("📋 Active Medications")
        
        active_meds = {med_id: med for med_id, med in tracker.medications.items() if med['active']}
        
        if not active_meds:
            st.info("No active medications found. Add a medication to get started!")
        else:
            for med_id, med in active_meds.items():
                with st.expander(f"💊 **{med['name']}** ({med['dosage']}) - {med['frequency']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Schedule:** {', '.join(med['times'])}")
                        if med['notes']:
                            st.write(f"**Notes:** {med['notes']}")
                        st.write(f"**Added:** {datetime.fromisoformat(med['created_date']).strftime('%Y-%m-%d %H:%M')}")
                        
                        
                        med_side_effects = [se for se in tracker.side_effects if se['med_id'] == med_id]
                        st.write(f"**Side Effects Reported:** {len(med_side_effects)}")
                    
                    with col2:
                        st.write("**Actions:**")
                        
                        
                        archive_reason = st.selectbox(
                            "Archive reason:",
                            ["", "Course completed", "Medication changed", "Side effects", "Doctor's instruction", "Other"],
                            key=f"archive_reason_{med_id}"
                        )
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("📁 Archive", key=f"archive_{med_id}", use_container_width=True):
                                if archive_reason:
                                    tracker.archive_medication(med_id, archive_reason)
                                    st.success(f"✅ {med['name']} archived!")
                                    st.rerun()
                                else:
                                    st.error("Please select an archive reason.")
                        
                        with col_b:
                            if st.button("🗑️ Delete", key=f"delete_{med_id}", use_container_width=True, type="secondary"):
                                
                                st.session_state[f'confirm_delete_{med_id}'] = True
                        
                       
                        if st.session_state.get(f'confirm_delete_{med_id}', False):
                            st.warning("⚠️ **Delete Confirmation**")
                            st.write("This will permanently delete:")
                            st.write(f"- Medication: {med['name']}")
                            st.write(f"- All side effects ({len([s for s in tracker.side_effects if s['med_id'] == med_id])} entries)")
                            
                            col_confirm, col_cancel = st.columns(2)
                            
                            with col_confirm:
                                if st.button("✅ Confirm Delete", key=f"confirm_del_{med_id}", type="primary"):
                                    
                                    tracker.side_effects = [se for se in tracker.side_effects if se['med_id'] != med_id]
                                    tracker.delete_medication(med_id)
                                    st.success(f"✅ {med['name']} and all associated data deleted!")
                                    if f'confirm_delete_{med_id}' in st.session_state:
                                        del st.session_state[f'confirm_delete_{med_id}']
                                    st.rerun()
                            
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_del_{med_id}"):
                                    del st.session_state[f'confirm_delete_{med_id}']
                                    st.rerun()
    
    with tab2:
        st.subheader("📦 Archived Medications")
        
        archived_meds = {med_id: med for med_id, med in tracker.medications.items() if not med['active']}
        
        if not archived_meds:
            st.info("No archived medications found.")
        else:
            for med_id, med in archived_meds.items():
                with st.expander(f"📦 **{med['name']}** ({med['dosage']}) - ARCHIVED"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Schedule:** {', '.join(med['times'])}")
                        if med['notes']:
                            st.write(f"**Notes:** {med['notes']}")
                        st.write(f"**Added:** {datetime.fromisoformat(med['created_date']).strftime('%Y-%m-%d %H:%M')}")
                        
                        if 'archived_date' in med:
                            st.write(f"**Archived:** {datetime.fromisoformat(med['archived_date']).strftime('%Y-%m-%d %H:%M')}")
                        if 'archive_reason' in med:
                            st.write(f"**Reason:** {med['archive_reason']}")
                        
                        
                        total_side_effects = [se for se in tracker.side_effects if se['med_id'] == med_id]
                        
                        if total_side_effects:
                            st.write(f"**Side Effects Reported:** {len(total_side_effects)}")
                    
                    with col2:
                        st.write("**Actions:**")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("🔄 Reactivate", key=f"reactivate_{med_id}", use_container_width=True):
                                tracker.reactivate_medication(med_id)
                                st.success(f"✅ {med['name']} reactivated!")
                                st.rerun()
                        
                        with col_b:
                            if st.button("🗑️ Delete", key=f"delete_arch_{med_id}", use_container_width=True, type="secondary"):
                                st.session_state[f'confirm_delete_arch_{med_id}'] = True
                        
                        
                        if st.session_state.get(f'confirm_delete_arch_{med_id}', False):
                            st.warning("⚠️ **Permanent Delete**")
                            st.write("This will permanently remove all data for this medication.")
                            
                            col_confirm, col_cancel = st.columns(2)
                            
                            with col_confirm:
                                if st.button("✅ Confirm", key=f"confirm_del_arch_{med_id}", type="primary"):
                                    tracker.side_effects = [se for se in tracker.side_effects if se['med_id'] != med_id]
                                    tracker.delete_medication(med_id)
                                    st.success(f"✅ {med['name']} permanently deleted!")
                                    if f'confirm_delete_arch_{med_id}' in st.session_state:
                                        del st.session_state[f'confirm_delete_arch_{med_id}']
                                    st.rerun()
                            
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_del_arch_{med_id}"):
                                    del st.session_state[f'confirm_delete_arch_{med_id}']
                                    st.rerun()
    
    with tab3:
        st.subheader("🔧 Bulk Actions")
        
        st.write("**Bulk Operations:**")
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Archive Multiple Medications**")
            if st.button("📁 Archive Completed Medications", help="Archive medications that no longer need to be taken"):
                
                st.info("Use the individual Archive buttons in the Active Medications tab to archive completed medications.")
        
        with col2:
            st.write("**Data Cleanup**")
            if st.button("🧹 Clean Old Data", help="Remove side effects older than 1 year"):
                cutoff_date = datetime.now() - timedelta(days=365)
                original_side_effect_count = len(tracker.side_effects)
                
                
                tracker.side_effects = [se for se in tracker.side_effects if 
                                       datetime.fromisoformat(se['timestamp']) >= cutoff_date]
                
                tracker.save_data()
                
                se_removed = original_side_effect_count - len(tracker.side_effects)
                
                st.success(f"✅ Cleaned old data: {se_removed} side effects removed")
                st.rerun()
        
       
        st.markdown("---")
        st.write("**Database Statistics:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            active_count = len([m for m in tracker.medications.values() if m['active']])
            st.metric("Active Meds", active_count)
        
        with col2:
            archived_count = len([m for m in tracker.medications.values() if not m['active']])
            st.metric("Archived Meds", archived_count)


elif page == "Side Effects":
    st.header("⚠️ Side Effects Tracking")
    
    active_meds = {med_id: med for med_id, med in tracker.medications.items() if med['active']}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Report Side Effect")
        
        if not active_meds:
            st.warning("No active medications found.")
        else:
            
            med_options_map = {
                f"{med['name']} ({med['dosage']})": med_id 
                for med_id, med in active_meds.items()
            }
            med_display_names = list(med_options_map.keys())
            
            with st.form("side_effect_log"):
                
                selected_med_display = st.selectbox(
                    "Which medication?", 
                    options=med_display_names,
                    key="medication_selector"
                )
                
               
                selected_med_id = med_options_map.get(selected_med_display)
                
                effect = st.text_input("Side Effect", placeholder="e.g., Headache, Nausea, Dizziness")
                
                severity = st.select_slider("Severity", 
                                          options=[1, 2, 3, 4, 5],
                                          format_func=lambda x: {
                                              1: "😐 Mild", 2: "😕 Moderate", 3: "😣 Significant", 
                                              4: "😰 Severe", 5: "🚨 Very Severe"
                                          }[x])
                
                effect_notes = st.text_area("Additional Details", 
                                          placeholder="When did it start? Duration? What helps?")
                
                submitted = st.form_submit_button("Report Side Effect", use_container_width=True)
                
                if submitted:
                    if effect and selected_med_id:
                        tracker.log_side_effect(selected_med_id, effect, severity, effect_notes)
                        st.success("✅ Side effect reported successfully!")
                        st.rerun()
                    elif not effect:
                        st.error("Please describe the side effect.")
                    else:
                        st.error("Please select a medication.")
    
    with col2:
        st.subheader("Side Effect History")
        
        if tracker.side_effects:
            for effect in sorted(tracker.side_effects, key=lambda x: x['timestamp'], reverse=True)[:10]:
                
                med_info = tracker.medications.get(effect['med_id'])
                med_name = med_info['name'] if med_info else "Unknown (Deleted)"
                
                severity_display = {
                    1: "😐 Mild", 2: "😕 Moderate", 3: "😣 Significant", 
                    4: "😰 Severe", 5: "🚨 Very Severe"
                }[effect['severity']]
                
                timestamp = datetime.fromisoformat(effect['timestamp']).strftime("%Y-%m-%d %H:%M")
                
                with st.expander(f"**{effect['effect']}** - {med_name} ({timestamp})"):
                    st.write(f"**Severity:** {severity_display}")
                    if effect['notes']:
                        st.write(f"**Notes:** {effect['notes']}")
        else:
            st.info("No side effects reported yet.")


elif page == "Analytics":
    st.header("📊 Analytics & Insights")
    
    
    st.subheader("⚠️ Side Effects Analytics")
    
    if tracker.side_effects:
        col1, col2 = st.columns(2)
        
        with col1:
            
            side_effect_data = []
            for effect in tracker.side_effects:
                date = datetime.fromisoformat(effect['timestamp']).date()
                side_effect_data.append({
                    'date': date,
                    'severity': effect['severity'],
                    'effect': effect['effect']
                })
            
            df_side_effects = pd.DataFrame(side_effect_data)
            
           
            daily_counts = df_side_effects.groupby('date').size().reset_index()
            daily_counts.columns = ['date', 'count']
            
            fig = px.line(daily_counts, x='date', y='count',
                         title='Side Effects Over Time',
                         labels={'count': 'Number of Side Effects', 'date': 'Date'})
            fig.update_traces(line_color='#FF6B6B', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
           
            severity_counts = df_side_effects['severity'].value_counts().reset_index()
            severity_counts.columns = ['severity', 'count']
            severity_mapping = {1: "Mild", 2: "Moderate", 3: "Significant", 4: "Severe", 5: "Very Severe"}
            severity_counts['severity_label'] = severity_counts['severity'].replace(severity_mapping)
            
            fig = px.pie(severity_counts, values='count', names='severity_label',
                        title='Side Effects by Severity')
            st.plotly_chart(fig, use_container_width=True)
        
        
        st.subheader("💊 Medication Side Effect Analysis")
        
        med_analysis = {}
        for effect in tracker.side_effects:
            med_id = effect['med_id']
            
            med_info = tracker.medications.get(med_id)
            med_name = med_info['name'] if med_info else "Unknown (Deleted)"
            
            if med_name not in med_analysis:
                med_analysis[med_name] = {
                    'total_effects': 0,
                    'avg_severity': 0,
                    'severities': []
                }
            
            med_analysis[med_name]['total_effects'] += 1
            med_analysis[med_name]['severities'].append(effect['severity'])
        
   
        for med_name, data in med_analysis.items():
            data['avg_severity'] = sum(data['severities']) / len(data['severities'])
        
        if med_analysis:
            analysis_data = []
            for med_name, data in med_analysis.items():
                analysis_data.append({
                    'Medication': med_name,
                    'Total Side Effects': data['total_effects'],
                    'Average Severity': round(data['avg_severity'], 1)
                })
            
            df_analysis = pd.DataFrame(analysis_data)
            st.dataframe(df_analysis, use_container_width=True)
        
    else:
        st.info("No side effect data available for analysis.")
    
   
    if tracker.mood_logs:
        st.subheader("😊 Mood Analytics")
        
        
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_moods = [mood for mood in tracker.mood_logs if datetime.fromisoformat(mood['timestamp']) >= cutoff_date]
        mood_data = sorted(recent_moods, key=lambda x: x['timestamp'])
        
        if mood_data:
            df_mood = pd.DataFrame(mood_data)
            df_mood['timestamp'] = pd.to_datetime(df_mood['timestamp'])
            df_mood['date'] = df_mood['timestamp'].dt.date
            
            fig = px.line(df_mood, x='date', y='mood_score', 
                         title='30-Day Mood Trend',
                         labels={'mood_score': 'Mood Score (1-10)', 'date': 'Date'})
            fig.update_traces(line_color='#2E8B57', line_width=3)
            fig.update_layout(yaxis_range=[1, 10])
            st.plotly_chart(fig, use_container_width=True)
            
            
            avg_mood = df_mood['mood_score'].mean()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Mood", f"{avg_mood:.1f}/10")
            with col2:
                mood_count = len(df_mood)
                st.metric("Mood Entries", mood_count)


st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Notifications")

notification_js = """
<script>
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                new Notification('MediTracker Pro', {
                    body: 'Notifications enabled! You will receive medication reminders.',
                    icon: '💊'
                });
            }
        });
    }
}

function scheduleReminders() {
    // This would normally connect to a backend service
    // For demo purposes, we'll show how it could work
    console.log('Medication reminders scheduled');
}
</script>
"""

if st.sidebar.button("Enable Browser Notifications"):
    import streamlit.components.v1 as components
    components.html(f"""
    {notification_js}
    <button onclick="requestNotificationPermission()" style="display:none;" id="notif-btn"></button>
    <script>document.getElementById('notif-btn').click();</script>
    """, height=0)
    st.sidebar.success("Notification permission requested!")


st.sidebar.markdown("---")
st.sidebar.subheader("📥 Data Management")

if st.sidebar.button("Export Data"):
    data = {
        'medications': tracker.medications,
        'logs': tracker.logs,
        'mood_logs': tracker.mood_logs,
        'side_effects': tracker.side_effects,
        'export_date': datetime.now().isoformat()
    }
    
    st.sidebar.download_button(
        label="Download JSON",
        data=json.dumps(data, indent=2, default=str),
        file_name=f"meditracker_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>💊 MediTracker Pro - Your Smart Medication Companion</p>
    <p><small>Remember: This app is for tracking purposes only. Always consult healthcare professionals for medical advice.</small></p>
</div>
""", unsafe_allow_html=True)
