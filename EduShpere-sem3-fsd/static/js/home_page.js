const user_name_field = document.getElementById('page_user_name')

const enroll_count = document.getElementById('enroll_count')
const complete_count = document.getElementById('complete_count')
const certi_count = document.getElementById('certi_count')

const user_enrolled = document.getElementsByClassName('enrolled-courses-list')
const course_diplay = document.getElementsByClassName('recommended-course')
const user_progress_score = document.getElementsByClassName('progress-score')

// to display box when no course is there------------
const course_area  = document.getElementsByClassName('course_area')

// to show message to the user-----------------------
// show message to the user
function info_msg(msg, color = 'info') {
    const mssg = `
        <div class="alert alert-${color} alert-dismissible position-absolute mt-5 start-50 translate-middle fade show w-50"
             style="z-index:1055;">
            ${msg}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', mssg)

    // to remove error after 1second-------------
    location.reload()
    setTimeout(() => {
        const alertEl = document.querySelector('.alert')
        if (alertEl) {
            bootstrap.Alert.getOrCreateInstance(alertEl).close()
        }
        // refresh whole page after 1 second
    }, 1000)
}


// to set user_name for the page--------------
function setUserName(user_name=null) {
    user_name_field.innerText = user_name
}


function setUserProgress(score) {
    for (let i = 0; i < score.length; i++) {
        user_progress_score[i].innerText = score[i]
        
    }
}

// setUserProgress([1,2,3])


// to add the list of course that are enrolled bu users-----------------------------------
function showUserCourse(coursename,progress,course_id) {
    const en_course = `
    <div class="enrolled-courses">
        <img src="https://placehold.co/100x100/png?text=${coursename.slice(0,2)}" alt="Course" class="enrolled-courses-img rounded-3">
        <div class="en-course-details">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <span style="font-weight: 700; font-size: 1.1rem;">${coursename}</span>
                <span class="badge bg-primary bg-opacity-10 text-primary">Active</span>
            </div>
            <div class="progress-bar">
                <div class="bar-stick" style="width: ${Math.trunc(progress)}%;"></div>
            </div>
            <div class="d-flex justify-content-between mt-2">
                <span style="font-size: 0.85rem; color: #64748b;">${progress.toFixed(2)}% completed</span>   
            </div>
            <button class="btn btn-primary btn-sm mt-3 w-100 rounded-pill" course_id=${course_id} onclick='startLearning(this)'>Continue Learning <i class="bi bi-arrow-right"></i></button>
        </div>
    </div>
    `

    user_enrolled[0].insertAdjacentHTML('beforeend',en_course)
}

// to use method-------------
// showUserCourse('Python Programming',90)


// to add general courses list----------------------------------------------------
function showRecommendedCourses(coursename,owner,price,course_id) {
    const course_card = `
    <div class="course-card">
        <div class="position-relative">
            <img src="https://placehold.co/400x250/png?text=${coursename.split()}" alt="" class="course-image">
        </div>
        <div class="p-3 d-flex flex-column h-100">
            <span class="course-title">${coursename}</span>

            <span class="course-author text-muted small mt-1">by ${owner}</span>
            
            <div class="d-flex justify-content-between align-items-center mt-3">
                <span class="review">
                    <i class="bi bi-star-fill"></i> 4.8 <span class="text-muted ms-1">(1.2k)</span>
                </span>

                <span class="course-price">💎 ${price}</span>
            </div>
            
            <button class="btn btn-outline-primary mt-2 w-100 fw-bold" course_id=${course_id} onclick="EnrollCourse(this)">Enroll Now</button>
        </div>
    </div>
    `

    course_diplay[0].insertAdjacentHTML('beforeend',course_card)
}

// to use method-------------
// showRecommendedCourses('Full Stack','xyz',1500)


// to get user name ----------------
fetch('/user/data').then(e => e.json())
.then(data => setUserName(data.name))


// to get user_enrolled courses data-------------------
fetch('/user_courses/data').then(e => e.json())
.then(data => {
    enroll_count.innerText = data.length-2
    complete_count.innerText = data[data.length-2].completed
    certi_count.innerText = data[data.length-1].certificate_count

    // console.log(data)
    if (data.length<3) {
        course_area[0].classList.remove('d-none')
        return
    }
    course_area[0].classList.add('d-none')
    for (let index = 0; index < data.length-2; index++) {
        key = data[index]
        showUserCourse(key.course_title,key.course_progress,key.course_id)
    }
})



// to get all course data-------------------
fetch('/courses/data').then(e => e.json())
.then(data => {
    if (data.length===0) {
        course_area[1].classList.remove('d-none')
        return
    }
    course_area[1].classList.add('d-none')
    // console.log(data)
    for (const key of data) {
        showRecommendedCourses(key.course_title,key.course_owner,key.course_price,key.course_id)
    }
})


// to add course to user data when enroll Now btn is clicked-----------
function EnrollCourse(btn) {
    course_id = btn.getAttribute('course_id')
    fetch("/enrollCourse", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            courseId: course_id
        })
    })
    .then(res => res.json())
    .then(data => {
        info_msg(data.message,'info')
    })
    .catch(err => console.error(err))
}

// to open the enrolled module page-----------------------------------
function startLearning(btn) {
    const course_id = btn.getAttribute('course_id')
    // to opne the page of that id--------
    window.location.href = `/myCourse/${course_id}`
}

// to open the all certificate list page-----------------------------------
function openCertificate_ls(btn) {
    const course_id = btn.getAttribute('course_id')
    // to opne the page of that id--------
    window.location.href = `/myCertificates/${course_id}`
}


// add points to user account when user click on btn-------------------------------
function buyPoints(btn) {
    const points_buy = btn.getAttribute('points')
    console.log(points_buy)
    fetch('/buyPackage',{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            points: points_buy
        })
    }).then (e=>e.json())
    .then(data => {
        info_msg(data.message,'success')
    })
    .catch(err => console.error(err))
}