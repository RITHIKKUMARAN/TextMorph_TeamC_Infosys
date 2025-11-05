import streamlit as st

def load_styles():
 st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Poppins', sans-serif;
    }

      body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        margin: 0;
        padding: 0;
      }

    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* --- Main Container --- */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
    }

    .login-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
        align-items: center;
        max-width: 1000px;
        width: 100%;
    }

    @media (max-width: 768px) {
        .login-container {
            grid-template-columns: 1fr;
            gap: 2rem;
        }
        .left-section {
            display: none;
        }
    }

    /* --- Left Section (Branding) --- */
    .left-section {
        color: white;
        text-align: left;
    }

    .brand-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, #ffffff 0%, #e0e0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .brand-subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
        font-weight: 300;
        line-height: 1.6;
    }

    .feature-list {
        list-style: none;
        padding: 0;
    }

    .feature-list li {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
    }

    .feature-list li:before {
        content: "✓";
        font-weight: 700;
        font-size: 1.3rem;
        margin-right: 0.8rem;
        color: #00d4ff;
    }

    /* --- Right Section (Login Card) --- */
    .right-section {
        display: flex;
        justify-content: center;
    }

    .login-card {
        background: transparent;
        backdrop-filter: none;
        border-radius: 20px;
        padding: 3rem;
        width: 100%;
        max-width: 400px;
        box-shadow: none;
        border: none;
    }

    .card-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .card-subtitle {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 2rem;
    }

    /* --- Form Elements --- */
    .form-group {
        margin-bottom: 1.5rem;
    }

    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
        background-color: rgba(255, 255, 255, 0.3);
    }

    .stTextInput > label {
        color: #ffffff;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        display: block;
    }

    /* --- Button --- */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.9rem;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button:disabled {
        background: linear-gradient(135deg, #ccc 0%, #999 100%);
        box-shadow: none;
    }

    /* --- Footer Links --- */
    .form-footer {
        margin-top: 1.5rem;
        text-align: center;
        font-size: 0.9rem;
    }

    .forgot-password {
        display: block;
        margin-bottom: 1rem;
    }

    .forgot-password a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }

    .forgot-password a:hover {
        color: #764ba2;
    }

    .signup-link {
        color: #666;
    }

    .signup-link a {
        color: #667eea;
        text-decoration: none;
        font-weight: 700;
        transition: color 0.3s ease;
    }

    .signup-link a:hover {
        color: #764ba2;
    }

    /* --- Divider --- */
    .divider {
        display: flex;
        align-items: center;
        margin: 2rem 0;
        color: #ccc;
        font-size: 0.85rem;
    }

    .divider:before,
    .divider:after {
        content: "";
        flex: 1;
        height: 1px;
        background: #e8ebf5;
    }

    .divider:before {
        margin-right: 1rem;
    }

    .divider:after {
        margin-left: 1rem;
    }

    </style>
    """, unsafe_allow_html=True)


def render_login_ui():
    load_styles()
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # --- Left Section (Branding) ---
    st.markdown("""
    <div class="left-section">
        <div class="brand-title">TextMorph</div>
    </div>
    """, unsafe_allow_html=True)
       
    st.markdown('<h2 class="card-title">Welcome Back</h2>', unsafe_allow_html=True)
    
    email = st.text_input("Email or Username", placeholder="Enter your email or username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    login_clicked = st.button("Log In", use_container_width=True)
    
    st.markdown("""
    <div class="form-footer">
        <a class="forgot-password" href="#">Forgot password?</a>
        <p class="signup-link">Don't have an account? <a href="?register">Sign up</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # End of login-card
    st.markdown('</div>', unsafe_allow_html=True)  # End of right-section
    st.markdown('</div>', unsafe_allow_html=True)  # End of login-container
    st.markdown('</div>', unsafe_allow_html=True)  # End of login-wrapper
    
    return email, password, login_clicked


def render_register_ui():
    load_styles()
    
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # --- Left Section (Branding) ---
    st.markdown("""
    <div class="left-section">
        <div class="brand-title">TextMorph</div>
        <p class="brand-subtitle">Join us today and unlock powerful text tools</p>
        <ul class="feature-list">
            <li>Get started in seconds</li>
            <li>No credit card required</li>
            <li>Full access to all features</li>
            <li>Join our community</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Right Section (Register Form) ---
    st.markdown('<div class="right-section">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    st.markdown('<h2 class="card-title">Create Account</h2>', unsafe_allow_html=True)
    st.markdown('<p class="card-subtitle">Join TextMorph today</p>', unsafe_allow_html=True)
    
    email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
    password = st.text_input("Password", type="password", placeholder="Create a strong password", key="reg_pass")
    confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="reg_confirm")
    
    register_clicked = st.button("Sign Up", use_container_width=True)
    
    st.markdown("""
    <div class="form-footer">
        <p class="signup-link">Already have an account? <a href="?login">Log in</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # End of login-card
    st.markdown('</div>', unsafe_allow_html=True)  # End of right-section
    st.markdown('</div>', unsafe_allow_html=True)  # End of login-container
    st.markdown('</div>', unsafe_allow_html=True)  # End of login-wrapper
    
    return email, password, confirm, register_clicked