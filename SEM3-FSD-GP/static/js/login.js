const title = document.querySelector('.form-title')
const btn = document.getElementById('btn')
const submit_btn = document.getElementById('sub_btn')


const form = document.querySelector('form')
const user_email = document.getElementById('user_email')
const user_pass = document.getElementById('user_pass')

// to display errors-------------------
const email_error = document.getElementById('email_error')
const pass_error = document.getElementById('pass_error')
const main_error = document.getElementById('main_error')

// to get mode of the form is it is signup or signin---------------
const form_mode = document.getElementById('form_mode').value

// to store user_data-------------------------
user_data = {}

let signup = false;
if (form_mode === 'signup'){
    if (!document.getElementById('name-field')) {
        form.insertAdjacentHTML('afterbegin',
            `
            <div id="name-field">
                <label for="name">Name</label>
                <input type="name" placeholder="name" id="user_name" name="user_name" required>
                <span class="error" id="name_error">Invalid Name!!!</span>
            </div>
            `
        )
    }
    submit_btn.innerText = 'Sign up'
    btn.innerText = 'Sign in'
    signup = true
}

btn.addEventListener('click',() => {
    signup = !signup
    
    // when signup page-------------
    if (signup) {
        main_error.innerText = ''
        title.innerHTML = 'Create Account'

        // to add name input filed for signup page---------------------
        if (!document.getElementById('name-field')) {
            form.insertAdjacentHTML('afterbegin',
                `
                <div id="name-field">
                    <label for="name">Name</label>
                    <input type="name" placeholder="name" id="user_name" name="user_name" required>
                    <span class="error" id="name_error">Invalid Name!!!</span>
                </div>
                `
            )
        }
        submit_btn.innerText = 'Sign up'
        btn.innerText = 'Sign in'
    }

    // when signin page----------------
    else {
        main_error.innerText = ''
        title.innerHTML = 'Welcome Back'

        // to remove name user field----------
        const nameField = document.getElementById('name-field')
        if (nameField) {
            nameField.remove()
        }
        submit_btn.innerText = 'Sign in'
        btn.innerText = 'Sign up'
    }

})


// regex verification---------------
const name_reg = /^[A-Za-z]{3,}$/
const email_reg = /^(?=.{13,}$)[A-Za-z.%+-]+@gmail.com$/
const pass_reg = /^[A-Za-z0-9@_]{6,8}$/

// to do form validation-------------------
form.addEventListener('submit', (e) => {
    e.preventDefault()

    let error = false
    user_data = {}


    // Name validation (only for signup)--------------------------
    if (document.getElementById('name-field')) {

        const user_name = document.getElementById('user_name')
        const name_error = document.getElementById('name_error')

        if (name_reg.test(user_name.value.trim())) {
            user_data.name = user_name.value
            name_error.classList.remove('show_error')
        } else {
            name_error.classList.add('show_error')
            error = true
        }
    }

    // Email validation----------------
    if (email_reg.test(user_email.value)) {
        user_data.email = user_email.value
        email_error.classList.remove('show_error')
    } else {
        email_error.classList.add('show_error')
        error = true
    }

    // Password validation--------------------
    if (pass_reg.test(user_pass.value)) {
        user_data.password = user_pass.value
        if (user_pass.value.length<6 || user_pass.value.length>8) {
            pass_error.innerText = 'Password Length Must be Between 6 to 8'
        }
        else {
            pass_error.innerText = 'In-Valid Password Formate!!!'
        }
        pass_error.classList.remove('show_error')
    } else {
        pass_error.classList.add('show_error')
        error = true
    }

    if (!error) {
        form.submit()
    }  
})