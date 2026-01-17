import streamlit as st
from datetime import datetime
import requests
import json
import os

# Page configuration
st.set_page_config(
    page_title="Founder's Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional design
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #1f2937;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #374151;
    }
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# File path for persistent storage
TASKS_FILE = "tasks_data.json"

def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    except IOError:
        st.error("⚠️ Could not save tasks to file")

# Initialize session state
if 'founder_name' not in st.session_state:
    st.session_state.founder_name = ""
if 'status' not in st.session_state:
    st.session_state.status = "Deep Work"
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()
if 'timer_minutes' not in st.session_state:
    st.session_state.timer_minutes = 25
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'timer_start_time' not in st.session_state:
    st.session_state.timer_start_time = None
if 'timer_end_time' not in st.session_state:
    st.session_state.timer_end_time = None
if 'coding_log' not in st.session_state:
    st.session_state.coding_log = ""
if 'current_quote' not in st.session_state:
    st.session_state.current_quote = None

# Sidebar
with st.sidebar:
    st.markdown("## 👤 Profile")
    st.markdown("---")
    
    # Name input
    founder_name = st.text_input(
        "Your Name",
        value=st.session_state.founder_name,
        placeholder="Enter your name",
        key="name_input"
    )
    st.session_state.founder_name = founder_name
    
    st.markdown("---")
    
    # Status selector
    st.markdown("### 📊 Status")
    status_options = {
        "Deep Work": "🎯",
        "Learning": "📚",
        "Resting": "😌"
    }
    
    selected_status = st.selectbox(
        "Current Status",
        options=list(status_options.keys()),
        index=list(status_options.keys()).index(st.session_state.status) if st.session_state.status in status_options else 0,
        key="status_select"
    )
    st.session_state.status = selected_status
    
    # Display status badge
    status_emoji = status_options[selected_status]
    status_colors = {
        "Deep Work": "#3b82f6",
        "Learning": "#10b981",
        "Resting": "#f59e0b"
    }
    status_color = status_colors.get(selected_status, "#6b7280")
    
    st.markdown(
        f'<div class="status-badge" style="background-color: {status_color}20; color: {status_color}; border: 1px solid {status_color}40;">'
        f'{status_emoji} {selected_status}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("### 💡 Quick Stats")
    completed_tasks = sum(1 for task in st.session_state.tasks if task.get('completed', False))
    total_tasks = len(st.session_state.tasks)
    if total_tasks > 0:
        completion_rate = int((completed_tasks / total_tasks) * 100)
        st.metric("Tasks Completed", f"{completed_tasks}/{total_tasks}", f"{completion_rate}%")
    else:
        st.metric("Tasks Completed", "0/0", "0%")

# Main content area
st.markdown('<h1 class="main-header">🚀 Founder\'s Dashboard</h1>', unsafe_allow_html=True)

# Three Column Layout: Weather | Timer | To-Do List
col_weather, col_timer, col_todo = st.columns(3)

# Left Column: Live Weather
with col_weather:
    st.markdown('<div class="section-header">🌡️ Live Weather</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    city_input = st.text_input(
        "Enter city name",
        placeholder="e.g., New York, London, Tokyo",
        key="city_input",
        label_visibility="collapsed"
    )
    
    if city_input:
        try:
            # Use wttr.in API
            url = f"https://wttr.in/{city_input}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                temp_c = current['temp_C']
                condition = current['weatherDesc'][0]['value']
                
                # Weather emoji mapping
                weather_emojis = {
                    'Sunny': '☀️',
                    'Clear': '☀️',
                    'Partly cloudy': '⛅',
                    'Cloudy': '☁️',
                    'Overcast': '☁️',
                    'Rain': '🌧️',
                    'Rainy': '🌧️',
                    'Light rain': '🌦️',
                    'Heavy rain': '🌧️',
                    'Thunderstorm': '⛈️',
                    'Snow': '❄️',
                    'Fog': '🌫️',
                    'Mist': '🌫️'
                }
                
                # Find matching emoji
                weather_emoji = '🌤️'  # default
                for key, emoji in weather_emojis.items():
                    if key.lower() in condition.lower():
                        weather_emoji = emoji
                        break
                
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; 
                                border-radius: 0.75rem; 
                                color: white; 
                                text-align: center;'>
                        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>{weather_emoji}</div>
                        <div style='font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;'>{temp_c}°C</div>
                        <div style='font-size: 1.1rem; opacity: 0.9;'>{condition}</div>
                        <div style='font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;'>{city_input.title()}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error("❌ Could not fetch weather data. Please check the city name.")
        except Exception as e:
            st.error(f"❌ Error fetching weather: {str(e)}")
    else:
        st.info("📍 Enter a city name above to see the weather")

# Middle Column: Focus Timer
with col_timer:
    st.markdown('<div class="section-header">⏱️ Focus Timer</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    timer_minutes = st.slider(
        "Set timer duration (minutes)",
        min_value=5,
        max_value=120,
        value=st.session_state.timer_minutes,
        step=5,
        key="timer_slider"
    )
    st.session_state.timer_minutes = timer_minutes
    
    col_timer_btn1, col_timer_btn2 = st.columns(2)
    
    with col_timer_btn1:
        if st.button("▶️ Start", key="start_timer", use_container_width=True):
            st.session_state.timer_running = True
            st.session_state.timer_start_time = datetime.now()
            st.session_state.timer_end_time = st.session_state.timer_start_time.timestamp() + (timer_minutes * 60)
            st.rerun()
    
    with col_timer_btn2:
        if st.button("⏹️ Stop", key="stop_timer", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_start_time = None
            st.session_state.timer_end_time = None
            st.rerun()
    
    # Timer countdown display
    if st.session_state.timer_running and st.session_state.timer_end_time:
        current_time = datetime.now().timestamp()
        remaining = st.session_state.timer_end_time - current_time
        
        if remaining > 0:
            minutes_left = int(remaining // 60)
            seconds_left = int(remaining % 60)
            
            # Create a visual countdown
            progress = 1 - (remaining / (st.session_state.timer_minutes * 60))
            
            st.progress(progress)
            st.markdown(
                f"<div style='text-align: center; font-size: 2rem; font-weight: bold; color: #3b82f6; padding: 1rem;'>"
                f"⏳ {minutes_left:02d}:{seconds_left:02d}"
                f"</div>",
                unsafe_allow_html=True
            )
            
            # Auto-refresh when timer is running
            st.rerun()
        else:
            st.success("🎉 Timer complete! Great focus session!")
            st.balloons()
            st.session_state.timer_running = False
            st.session_state.timer_start_time = None
            st.session_state.timer_end_time = None
    else:
        st.info(f"⏸️ Timer ready - Set for {timer_minutes} minutes")

# Right Column: Daily Checklist (To-Do List)
with col_todo:
    st.markdown('<div class="section-header">✅ Daily Checklist</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Add new task
    new_task = st.text_input(
        "Add a new task",
        placeholder="Enter task description...",
        key="new_task_input",
        label_visibility="collapsed"
    )
    
    if st.button("➕ Add Task", key="add_task", use_container_width=True):
        if new_task.strip():
            st.session_state.tasks.append({
                'id': len(st.session_state.tasks),
                'text': new_task.strip(),
                'completed': False
            })
            save_tasks(st.session_state.tasks)
            st.rerun()
    
    # Display tasks
    if st.session_state.tasks:
        st.markdown("<br>", unsafe_allow_html=True)
        for idx, task in enumerate(st.session_state.tasks):
            completed = st.checkbox(
                task['text'],
                value=task['completed'],
                key=f"task_check_{task['id']}"
            )
            # Update task completion status and save if changed
            if st.session_state.tasks[idx]['completed'] != completed:
                st.session_state.tasks[idx]['completed'] = completed
                save_tasks(st.session_state.tasks)
            
            # Delete button inline
            if st.button("🗑️", key=f"delete_task_{task['id']}", help="Delete task"):
                st.session_state.tasks.pop(idx)
                save_tasks(st.session_state.tasks)
                st.rerun()
    else:
        st.info("📝 No tasks yet. Add your first task above!")

st.markdown("---")

# Daily Wisdom Section
st.markdown('<div class="section-header">💡 Daily Wisdom</div>', unsafe_allow_html=True)
st.markdown("---")

if st.button("✨ Get Inspired", key="get_quote", use_container_width=True):
    try:
        # Use quotable.io API for random quotes
        response = requests.get("https://api.quotable.io/random", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            quote_text = data['content']
            quote_author = data['author']
            st.session_state.current_quote = {
                'text': quote_text,
                'author': quote_author
            }
        else:
            st.error("❌ Could not fetch quote. Please try again.")
    except Exception as e:
        st.error(f"❌ Error fetching quote: {str(e)}")

# Display quote if available
if st.session_state.current_quote:
    quote = st.session_state.current_quote
    st.markdown(
        f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; 
                    border-radius: 0.75rem; 
                    color: white;'>
            <div style='font-size: 2rem; margin-bottom: 1rem; text-align: center;'>💭</div>
            <div style='font-size: 1.1rem; font-style: italic; line-height: 1.6; margin-bottom: 1rem; text-align: center;'>
                "{quote['text']}"
            </div>
            <div style='font-size: 0.95rem; font-weight: 600; text-align: right; opacity: 0.9;'>
                — {quote['author']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("💡 Click 'Get Inspired' to receive your daily dose of motivation!")

st.markdown("---")

# Coding Log Section
st.markdown('<div class="section-header">📝 Coding Log</div>', unsafe_allow_html=True)
st.markdown("---")

# Large text area for coding log
log_entry = st.text_area(
    "Document your learnings, insights, and breakthroughs",
    value=st.session_state.coding_log,
    height=300,
    placeholder="What did you learn today? What challenges did you overcome? What insights did you gain?\n\nWrite freely...",
    key="log_input",
    label_visibility="visible"
)
st.session_state.coding_log = log_entry

# Save and clear buttons
col_log1, col_log2 = st.columns([1, 1])
with col_log1:
    if st.button("💾 Save Notes", key="save_log", use_container_width=True):
        if log_entry.strip():
            st.success("✅ Notes saved!")
        else:
            st.warning("⚠️ Please enter some notes before saving!")

with col_log2:
    if st.button("🗑️ Clear", key="clear_log", use_container_width=True):
        st.session_state.coding_log = ""
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; padding: 2rem 0; font-size: 0.9rem;'>"
    "💼 Professional Dashboard | Keep building, keep learning, keep shipping 🚀"
    "</div>",
    unsafe_allow_html=True
)


