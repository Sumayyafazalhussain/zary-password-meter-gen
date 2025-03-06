import streamlit as st
import re
import random
import string
import math
from collections import defaultdict
from streamlit.components.v1 import html

# Page Configuration
st.set_page_config(
    page_title="PASSWORD-METER-generator",
    page_icon="🔑",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://cybershield.com/support',
        'Report a bug': "https://cybershield.com/bug",
        'About': "# Enterprise-grade Password Security Analysis"
    }
)

# Advanced CSS Styling
st.markdown("""
<style>
    :root {
        --primary: #6366f1;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --background: #0f172a;
        --surface:rgb(162, 163, 165);
    }

    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }

    .main {
        background: var(--background);
        color:rgb(248, 250, 252);
        padding: 2rem 1.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }

    .password-container {
        background: var(--surface);
        border-radius: 1rem;
        padding: 1.5rem;
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .strength-meter {
        height: 6px;
        border-radius: 3px;
        background: #334155;
        overflow: hidden;
        position: relative;
        margin: 1.5rem 0;
    }

    .strength-fill {
        height: 100%;
        width: 0;
        transition: all 0.4s ease;
        background: linear-gradient(90deg, var(--danger) 0%, var(--warning) 50%, var(--success) 100%);
    }

    .security-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        gap: 0.5rem;
    }

    .feedback-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        background: var(--surface);
        border-left: 4px solid transparent;
        transition: transform 0.2s ease;
    }

    .feedback-item:hover {
        transform: translateX(8px);
    }

    .generator-card {
        background: var(--surface);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }

    .toggle-group {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }

    .toggle-option {
        flex: 1;
        text-align: center;
        padding: 1rem;
        border-radius: 0.75rem;
        cursor: pointer;
        background: #334155;
        transition: all 0.3s ease;
    }

    .toggle-option.active {
        background: var(--primary);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Security Configuration
COMMON_PASSWORDS = set([
    'password', '123456', '123456789', 'qwerty', 'abc123',
    'password1', 'admin', 'letmein', 'welcome', 'monkey'
])

CHARACTER_SETS = {
    'lower': string.ascii_lowercase,
    'upper': string.ascii_uppercase,
    'digits': string.digits,
    'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?'
}

CRACK_TIME_THRESHOLDS = [
    (10**3, "Instant", "#ef4444"),
    (10**6, "Minutes", "#f59e0b"),
    (10**9, "Hours", "#eab308"),
    (10**12, "Days", "#84cc16"),
    (10**15, "Years", "#10b981"),
    (math.inf, "Centuries", "#6366f1")
]

def calculate_entropy(password):
    pool_size = 0
    if re.search(r'[a-z]', password): pool_size += 26
    if re.search(r'[A-Z]', password): pool_size += 26
    if re.search(r'[0-9]', password): pool_size += 10
    if re.search(r'[^A-Za-z0-9]', password): pool_size += 32
    return len(password) * math.log2(pool_size) if pool_size else 0

def estimate_crack_time(entropy):
    guesses_per_second = 1e12  # 1 trillion guesses/second
    seconds = (2 ** entropy) / guesses_per_second
    for threshold, label, color in CRACK_TIME_THRESHOLDS:
        if seconds < threshold:
            return label, color
    return "Centuries", "#6366f1"

def generate_password(length=16, **options):
    chars = ''
    chars += CHARACTER_SETS['lower'] if options.get('lower', True) else ''
    chars += CHARACTER_SETS['upper'] if options.get('upper', True) else ''
    chars += CHARACTER_SETS['digits'] if options.get('digits', True) else ''
    chars += CHARACTER_SETS['symbols'] if options.get('symbols', True) else ''
    
    if not chars:
        raise ValueError("At least one character set must be selected")
    
    return ''.join(random.choices(chars, k=length))

def analyze_password(password):
    analysis = {
        'length': len(password),
        'entropy': calculate_entropy(password),
        'checks': {
            'length': len(password) >= 12,
            'lower': bool(re.search(r'[a-z]', password)),
            'upper': bool(re.search(r'[A-Z]', password)),
            'digit': bool(re.search(r'[0-9]', password)),
            'symbol': bool(re.search(r'[^A-Za-z0-9]', password)),
            'repeats': not re.search(r'(.)\1{2}', password),
            'sequential': not re.search(r'(abc|123|xyz|987)', password.lower()),
            'common': password.lower() not in COMMON_PASSWORDS
        }
    }
    return analysis

def strength_assessment(analysis):
    score = 0
    max_score = 10
    
    # Length scoring
    if analysis['length'] >= 16: score += 3
    elif analysis['length'] >= 12: score += 2
    elif analysis['length'] >= 8: score += 1
    
    # Character diversity
    char_types = sum([analysis['checks']['lower'], 
                    analysis['checks']['upper'],
                    analysis['checks']['digit'],
                    analysis['checks']['symbol']])
    score += min(char_types * 1.5, 3)
    
    # Additional checks
    score += 1 if analysis['checks']['repeats'] else 0
    score += 1 if analysis['checks']['sequential'] else 0
    score += 2 if analysis['checks']['common'] else 0
    
    # Normalize score
    normalized = min(max(score / max_score * 100, 0), 100)
    
    # Determine strength level
    if normalized < 40: return normalized, "Weak", "#ef4444"
    elif normalized < 70: return normalized, "Moderate", "#f59e0b"
    elif normalized < 90: return normalized, "Strong", "#10b981"
    else: return normalized, "Very Strong", "#6366f1"

def password_input_section():
    st.markdown("""
    <div class="password-container">
        <h3 style="margin-top: 0; margin-bottom: 1rem;">🔑 Password Analysis</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    with col1:
        password = st.text_input(
            "Enter password to analyze:", 
            type="password",
            placeholder="Enter your password...",
            label_visibility="collapsed"
        )
    with col2:
        st.write("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("👁️", help="Toggle password visibility"):
            st.session_state.show_pass = not st.session_state.get('show_pass', False)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.get('show_pass', False) and password:
        st.markdown(f"""
        <div class="security-badge" style="margin: 1rem 0;">
            🔍 Visible Password: <code>{password}</code>
        </div>
        """, unsafe_allow_html=True)
    
    return password

def main():
    st.title(" 🔑password meter generator")
    st.caption("Enterprise-grade password security assessment powered by AI-driven threat analysis")
    
    password = password_input_section()
    
    if password:
        analysis = analyze_password(password)
        strength, label, color = strength_assessment(analysis)
        crack_time, crack_color = estimate_crack_time(analysis['entropy'])
        
        # Strength Meter
        st.markdown(f"""
        <div class="strength-meter">
            <div class="strength-fill" style="width: {strength}%"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Security Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="security-badge" style="border-color: {color}; color: {color}">
                ⚡ Strength: {label}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="security-badge" style="border-color: {crack_color}; color: {crack_color}">
                ⏳ Crack Time: {crack_time}
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="security-badge">
                🔢 Entropy: {analysis['entropy']:.1f} bits
            </div>
            """, unsafe_allow_html=True)
        
        # Security Feedback
        st.subheader("Security Assessment", anchor=False)
        checks = [
            ('length', 'Minimum 12 characters', '📏'),
            ('lower', 'Lowercase letters', '⓵'),
            ('upper', 'Uppercase letters', '⓶'),
            ('digit', 'Numeric characters', '➌'),
            ('symbol', 'Special characters', '➍'),
            ('repeats', 'No repeated patterns', '🔄'),
            ('sequential', 'No sequential strings', '🔀'),
            ('common', 'Not commonly used', '🛡️')
        ]
        
        cols = st.columns(2)
        for idx, (key, text, icon) in enumerate(checks):
            with cols[idx % 2]:
                status = analysis['checks'][key]
                bg_color = "#10b98120" if status else "#ef444420"
                border_color = "#10b981" if status else "#ef4444"
                st.markdown(f"""
                <div class="feedback-item" style="border-color: {border_color}; background: {bg_color}">
                    <span style="font-size: 1.2rem">{icon}</span>
                    <div>
                        <strong>{text}</strong><br>
                        <small>{"Pass" if status else "Fail"}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Password Generator
        with st.expander("🔧 Advanced Password Generator", expanded=True):
            with st.form("generator_form"):
                col1, col2 = st.columns(2)
                length = col1.slider("Password length", 8, 32, 16)
                col2.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
                options = {
                    'lower': col2.checkbox("Lowercase", True),
                    'upper': col2.checkbox("Uppercase", True),
                    'digits': col2.checkbox("Digits", True),
                    'symbols': col2.checkbox("Symbols", True)
                }
                
                if st.form_submit_button("✨ Generate Secure Password"):
                    try:
                        st.session_state.generated_pass = generate_password(length, **options)
                    except ValueError:
                        st.error("Please select at least one character set")
                
                if 'generated_pass' in st.session_state:
                    st.markdown(f"""
                    <div class="generator-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>Generated Password:</strong><br>
                                <code style="font-size: 1.4rem">{st.session_state.generated_pass}</code>
                            </div>
                            <button onclick="navigator.clipboard.writeText('{st.session_state.generated_pass}')" 
                                    style="background: var(--primary); border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; color: white; cursor: pointer;">
                                📋 Copy
                            </button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()