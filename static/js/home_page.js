const user_name_field = document.getElementById('page_user_name')

const enroll_count = document.getElementById('enroll_count')
const complete_count = document.getElementById('complete_count')
const certi_count = document.getElementById('certi_count')

const user_enrolled = document.getElementById('enrolled_courses_list')
const course_display = document.getElementById('recommended_course_list')
const user_progress_score = document.getElementsByClassName('progress-score')

const course_areas  = document.getElementsByClassName('course_area')

function info_msg(msg, type = 'success') {
    if (typeof showGlobalToast === 'function') {
        showGlobalToast(msg, type);
    } else {
        alert(msg);
    }
}

function setUserName(user_name=null) {
    if(user_name_field) user_name_field.innerText = user_name;
}

function showUserCourse(coursename, progress, course_id) {
    const en_course = `
    <div class="course-card">
        <div class="course-img-wrapper" style="background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(168,85,247,0.2))">
            <h1 class="text-white opacity-50 fw-bold m-0" style="font-size: 4rem;">${coursename.substring(0,2).toUpperCase()}</h1>
        </div>
        <div class="p-4 d-flex flex-column flex-grow-1">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <h5 class="fw-bold mb-0 text-truncate" title="${coursename}">${coursename}</h5>
                <span class="badge bg-primary bg-opacity-25 text-primary">Active</span>
            </div>
            
            <div class="mt-auto">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-secondary fw-semibold">Progress</small>
                    <small class="text-primary fw-bold">${progress.toFixed(0)}%</small>
                </div>
                <div class="progress" style="height: 6px; background: rgba(255,255,255,0.1);">
                    <div class="progress-bar bg-primary" role="progressbar" style="width: ${progress}%" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <button class="btn btn-outline-premium w-100 mt-4" course_id="${course_id}" onclick='startLearning(this)'>
                    Continue Learning <i class="bi bi-arrow-right"></i>
                </button>
            </div>
        </div>
    </div>
    `
    user_enrolled.insertAdjacentHTML('beforeend', en_course);
}

function showRecommendedCourses(coursename, owner, price, course_id) {
    const course_card = `
    <div class="course-card">
        <div class="course-img-wrapper" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(5,150,105,0.2))">
            <i class="bi bi-laptop" style="font-size: 4rem; color: rgba(255,255,255,0.2);"></i>
        </div>
        <div class="p-4 d-flex flex-column flex-grow-1">
            <h5 class="fw-bold mb-1 text-truncate" title="${coursename}">${coursename}</h5>
            <p class="text-secondary small mb-3">by <span class="text-white opacity-75">${owner}</span></p>
            
            <div class="d-flex align-items-center gap-1 mb-3">
                <i class="bi bi-star-fill text-warning" style="font-size:0.8rem;"></i>
                <i class="bi bi-star-fill text-warning" style="font-size:0.8rem;"></i>
                <i class="bi bi-star-fill text-warning" style="font-size:0.8rem;"></i>
                <i class="bi bi-star-fill text-warning" style="font-size:0.8rem;"></i>
                <i class="bi bi-star-half text-warning" style="font-size:0.8rem;"></i>
                <span class="text-secondary small ms-1">(4.8)</span>
            </div>
            
            <div class="mt-auto d-flex justify-content-between align-items-center pt-3 border-top" style="border-color: rgba(255,255,255,0.05)!important">
                <div class="fw-bold text-gradient"><i class="bi bi-gem me-1"></i> ${price} pts</div>
                <button class="btn btn-sm btn-premium" course_id="${course_id}" onclick="EnrollCourse(this)">Enroll</button>
            </div>
        </div>
    </div>
    `
    course_display.insertAdjacentHTML('beforeend', course_card);
}

fetch('/user/data').then(e => e.json())
.then(data => setUserName(data.name))

fetch('/user_courses/data').then(e => e.json())
.then(data => {
    if(enroll_count) enroll_count.innerText = data.length - 2;
    if(complete_count) complete_count.innerText = data[data.length-2].completed;
    if(certi_count) certi_count.innerText = data[data.length-1].certificate_count;

    if (data.length < 3) {
        course_areas[0].classList.remove('d-none');
        course_areas[0].style.gridColumn = "1 / -1";
        return;
    }
    course_areas[0].classList.add('d-none');
    for (let index = 0; index < data.length - 2; index++) {
        const key = data[index];
        showUserCourse(key.course_title, key.course_progress, key.course_id);
    }
})

fetch('/courses/data').then(e => e.json())
.then(data => {
    if (data.length === 0) {
        course_areas[1].classList.remove('d-none');
        course_areas[1].style.gridColumn = "1 / -1";
        return;
    }
    course_areas[1].classList.add('d-none');
    for (const key of data) {
        showRecommendedCourses(key.course_title, key.course_owner, key.course_price, key.course_id);
    }
})

function EnrollCourse(btn) {
    const course_id = btn.getAttribute('course_id')
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    fetch("/enrollCourse", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            courseId: course_id
        })
    })
    .then(res => res.json().then(data => ({status: res.status, body: data})))
    .then(({status, body}) => {
        if(status >= 400) {
            info_msg(body.error || body.message, 'error');
            btn.innerHTML = 'Enroll';
        } else {
            info_msg(body.message, 'success');
            setTimeout(() => location.reload(), 1500);
        }
    })
    .catch(err => {
        console.error(err);
        btn.innerHTML = 'Enroll';
    });
}

function startLearning(btn) {
    const course_id = btn.getAttribute('course_id')
    window.location.href = `/myCourse/${course_id}`
}

function openCertificate_ls(btn) {
    window.location.href = '/myCertificates'
}

function buyPoints(btn) {
    const points_buy = btn.getAttribute('points')
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    
    fetch('/buyPackage',{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            points: points_buy
        })
    }).then (res => res.json().then(data => ({status: res.status, body: data})))
    .then(({status, body}) => {
        if(status >= 400) {
            info_msg(body.error || body.message, 'error');
            btn.innerHTML = originalText;
        } else {
            info_msg(body.message, 'success');
            setTimeout(() => location.reload(), 1500);
        }
    })
    .catch(err => {
        console.error(err);
        btn.innerHTML = originalText;
    });
}