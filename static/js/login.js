document.addEventListener('DOMContentLoaded', () => {
    const title = document.getElementById('form-title');
    const subtitle = document.getElementById('form-subtitle');
    const toggleBtn = document.getElementById('btn');
    const submitBtn = document.getElementById('sub_btn');
    const toggleText = document.getElementById('toggle-text');
    const form = document.getElementById('authForm');
    
    const user_email = document.getElementById('user_email');
    const user_pass = document.getElementById('user_pass');
    
    const email_error = document.getElementById('email_error');
    const pass_error = document.getElementById('pass_error');
    
    const form_mode = document.getElementById('form_mode').value;
    const dynamicFields = document.getElementById('dynamic-fields');
    
    let isSignup = false;

    const buildSignupFields = () => {
        return `
            <div class="mb-3 position-relative" id="name-container">
                <div class="form-floating">
                    <input type="text" class="form-control premium-input" id="user_name" name="user_name" placeholder="John Doe" required>
                    <label for="user_name">Full Name</label>
                </div>
                <div class="error-text" id="name_error">Name must be at least 3 letters.</div>
            </div>
            <div class="form-check form-switch mb-3" id="role-container">
                <input class="form-check-input" type="checkbox" role="switch" id="roleCheck" name="roleCheck">
                <label class="form-check-label text-secondary" for="roleCheck">Sign up as an Institute</label>
            </div>
        `;
    };

    const setMode = (toSignup) => {
        isSignup = toSignup;
        if (isSignup) {
            title.innerText = 'Create Account';
            subtitle.innerText = 'Join EduSphere and start learning';
            submitBtn.innerText = 'Sign Up';
            toggleText.innerText = 'Already have an account?';
            toggleBtn.innerText = 'Sign In';
            
            if (dynamicFields.innerHTML.trim() === '') {
                dynamicFields.innerHTML = buildSignupFields();
            }
        } else {
            title.innerText = 'Welcome Back';
            subtitle.innerText = 'Please sign in to continue';
            submitBtn.innerText = 'Sign In';
            toggleText.innerText = 'Don\'t have an account?';
            toggleBtn.innerText = 'Sign Up';
            
            dynamicFields.innerHTML = ''; // Remove dynamically injected fields
        }
    };

    // Initialize mode
    if (form_mode === 'signup') {
        setMode(true);
    } else {
        setMode(false);
    }

    toggleBtn.addEventListener('click', () => {
        // Toggle the internal state
        setMode(!isSignup);
    });

    // Validation patterns
    const name_reg = /^[A-Za-z\s]{3,}$/;
    const email_reg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        let error = false;

        // Name Validation
        if (isSignup) {
            const user_name = document.getElementById('user_name');
            const name_error = document.getElementById('name_error');
            
            if (name_reg.test(user_name.value.trim())) {
                name_error.classList.remove('show_error');
            } else {
                name_error.classList.add('show_error');
                error = true;
            }
        }

        // Email Validation
        if (email_reg.test(user_email.value.trim())) {
            email_error.classList.remove('show_error');
        } else {
            email_error.classList.add('show_error');
            error = true;
        }

        // Password Validation
        if (isSignup) {
            const pass_reg = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$/;
            if (pass_reg.test(user_pass.value)) {
                pass_error.classList.remove('show_error');
            } else {
                pass_error.innerText = "Password must be at least 8 chars long with 1 Uppercase, 1 Lowercase, and 1 Number.";
                pass_error.classList.add('show_error');
                error = true;
            }
        } else {
            if (user_pass.value.trim().length > 0) {
                pass_error.classList.remove('show_error');
            } else {
                pass_error.innerText = "Password is required.";
                pass_error.classList.add('show_error');
                error = true;
            }
        }

        if (!error) {
            // Give button a loading state
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            submitBtn.disabled = true;
            form.submit();
        }
    });
});