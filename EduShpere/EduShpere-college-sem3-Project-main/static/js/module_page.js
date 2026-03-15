/* ===================== COURSE PART ===================== */
const course_title = document.getElementById('course-title')
const course_chapters_name = document.querySelector('#course-chapters')
const default_view = document.querySelector('.default-view')
const teaching_part = document.querySelector('.video-container')
const video_title = document.querySelector('#video-title')
const video_url = document.querySelector('iframe')
const chapter_overview = document.querySelector('#overview p')
const chapter_notes = document.querySelector('#notes_url')
const markCompleteBtn = document.querySelector('#markCompleteBtn')


// to show message to user---------
function info_msg(msg, color = 'info') {
    const mssg = `
        <div class="alert alert-${color} alert-dismissible position-absolute mt-5 start-50 translate-middle fade show w-50"
             style="z-index:1055;">
            ${msg}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `

    document.body.insertAdjacentHTML('afterbegin', mssg)

    // to remove error after 1second-------------
    setTimeout(() => {
        const alertEl = document.querySelector('.alert')
        if (alertEl) {
            bootstrap.Alert.getOrCreateInstance(alertEl).close()
        }
        location.reload()
    }, 1000)
}


const current_course = course_title.getAttribute('current_course_id');
let module_data = []

// Add chapter buttons
function add_courses_name(list) {
    list.forEach((name, index) => {
        course_chapters_name.insertAdjacentHTML(
            'beforeend',
            `
            <button class="list-group-item list-group-item-action d-flex align-items-center justify-content-between mb-2 rounded shadow-sm chapter-btn"
                chapter_id="${name[0]}">
                <span class="fw-semibold">
                    <i class="bi bi-pencil-square text-primary me-2"></i>
                    ${name[1]}
                </span>
                <span class="badge bg-light text-dark">▶</span>
            </button>
            `
        )
    })
}

function add_chapter_status() {
    fetch('/chapterStatus',{
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            courseId: current_course
        })
    })
    .then(res => res.json())
    .then(data => {
        const temp = []
        for (const element of data) {
            if (element.is_completed) {
                temp.push(element.chapter_id)
            }
        }
        const buttons = document.querySelectorAll('.chapter-btn')
        buttons.forEach((btn) => {
            // console.log(temp.includes(parseInt(btn.getAttribute('chapter_id'))))
            
            if (temp.includes(parseInt(btn.getAttribute('chapter_id')))) {
                btn.classList.add('border-success')
                btn.classList.add('bg-success-subtle')
                btn.querySelector('.badge').innerHTML = `
                    <i class="bi bi-check-circle-fill text-success"></i>
                `
            }
        })
    })
}

// Fetch course data
fetch(`/courseData/${current_course}`)
.then(res => res.json())
.then(data => {
    course_title.innerText = data[data.length - 1];
    let names = [];

    for (let i = 0; i < data.length - 1; i++) {
        module_data.push(data[i]);
        names.push([data[i].chapter_id, data[i].chapter_title]);
    }
    add_courses_name(names);
    add_chapter_status()
})

// to fetch chapter status-------




// Chapter click
course_chapters_name.addEventListener('click', e => {

    // to make chapter visible and test not-----------
    quiz_info_container.classList.add('d-none');
    default_view.classList.add('d-none');
    teaching_part.classList.remove('d-none');


    const chapter_id = parseInt(e.target.getAttribute('chapter_id'))
    const chapter = module_data.find(c => c.chapter_id === chapter_id)

    video_title.innerText = chapter.chapter_title
    video_url.src = `https://www.youtube.com/embed/${chapter.chapter_video.split('&')[0]}`
    chapter_overview.innerText = chapter.chapter_description
    chapter_notes.innerHTML = `<a href="${chapter.chapter_notes}" target="_blank"> Open Notes </a>`
    markCompleteBtn.setAttribute('chapter_id', chapter_id)
    teaching_part.style.visibility = 'visible'
});

// Mark complete
function markComplete(btn) {
    fetch("/chapterComplete", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            courseId: current_course,
            chapterId: btn.getAttribute('chapter_id')
        })
    })
    .then(res => res.json())
    .then(data => info_msg(data.message));
}



/* ===================== QUIZ PART ===================== */

const quiz_info_container = document.querySelector('.quiz-info-container')
const start_btn = document.getElementById('start_quiz')
const prev_btn = document.getElementById('prev_btn')
const next_btn = document.getElementById('next_btn')
const timerEl = document.getElementById('timer')
const attempt_left = document.getElementById('quiz_attempts')
const quiz_terms = document.querySelector('.quiz_terms')

// to update quiz ui-----------------
function quiz_progress(curr,total) {
    curr += 1
    document.getElementById('current_que').innerText = curr
    document.getElementById('total_que').innerText = total
    const perc = (curr/total)*100
    document.getElementById('quiz_progress').style.width = perc+'%'
}

const question_text = document.getElementById('question_text')
const radios = {
    A: document.getElementById('radio_a'),
    B: document.getElementById('radio_b'),
    C: document.getElementById('radio_c'),
    D: document.getElementById('radio_d')
};

function showQuizDetails() {
    teaching_part.classList.add('d-none')
    quiz_info_container.classList.remove('d-none')
    default_view.classList.add('d-none')
}

/* ---------- Quiz State ---------- */
let quizData = []
let pos = 0
let user_answer = []
let real_answer = []
let totalTime = 60
let timerInterval = null
let quizSubmitted = false

/* ---------- Load Question ---------- */
function loadQuestion(q, savedAns = null) {
    question_text.innerText = q.question_text

    document.getElementById('option_a').innerText = q.optiona
    document.getElementById('option_b').innerText = q.optionb
    document.getElementById('option_c').innerText = q.optionc
    document.getElementById('option_d').innerText = q.optiond

    Object.values(radios).forEach(r => r.checked = false)

    if (savedAns && radios[savedAns]) {
        radios[savedAns].checked = true
    }

    prev_btn.classList.toggle('d-none', pos === 0);
    next_btn.innerText = (pos === quizData.length - 1) ? 'Submit' : 'Next'
    // to update quiz progress bar----------
    quiz_progress(pos,real_answer.length)
}

/* ---------- Timer ---------- */
function startQuizTimer() {
    clearInterval(timerInterval)
    timerInterval = setInterval(() => {
        let m = Math.floor(totalTime / 60)
        let s = totalTime % 60
        timerEl.innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`

        if (totalTime-- <= 0) {
            submitQuiz();
        }
    }, 1000)
}

/* ---------- Submit ---------- */
function submitQuiz() {
    // console.log(user_answer)
    if (quizSubmitted) return
    quizSubmitted = true

    clearInterval(timerInterval)

    let correct = 0
    quizData.forEach((_, i) => {
        if (user_answer[i] === real_answer[i]) correct++
    });

    let score = (correct / quizData.length) * 100
    timerEl.innerHTML = `<div class="spinner-border fs-4" role="status"></div>`
    fetch('/quizFinished', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({courseId: current_course, score})
    }).then(e=>e.json())
    .then(data => {

        bootstrap.Modal.getInstance(document.getElementById('quiz_box')).hide()
        location.reload()
    })

}

/* ---------- Fetch Quiz ---------- */
fetch('/moduleQuiz', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({courseId: current_course})
})
.then(res => res.json())
.then(data => {
    const isAttempt = data[data.length - 1].isAttempt
    if (isAttempt) {
        quiz_terms.classList.add('d-none')
        start_btn.innerText = 'Attempt Finished!'
        attempt_left.innerText = 0
        // to stop the launch of modal when all attempts are over-------
        start_btn.removeAttribute('data-bs-toggle')
        return
    }

    quizData = data.slice(0, -1)
    real_answer = quizData.map(q => q.answer)
    console.log(real_answer)
    loadQuestion(quizData[pos]);

    start_btn.onclick = () => {
        totalTime = 60;
        quizSubmitted = false
        startQuizTimer()
    }

    document.querySelector('.modal-body').addEventListener('change', e => {
        if (e.target.name === 'quiz_option') {
            user_answer[pos] = e.target.value
        }
    })

    next_btn.onclick = () => {
        if (!user_answer[pos]) {
            alert('Select an option')
            return
        }
        if (pos === quizData.length - 1) {
            submitQuiz()
        } else {
            pos++
            loadQuestion(quizData[pos], user_answer[pos])
        }
    };

    prev_btn.onclick = () => {
        if (pos > 0) {
            pos--
            loadQuestion(quizData[pos], user_answer[pos])
        }
    };
});

// to show result report -----------------------
// is used in getResultData fetch method to show result data--
function showResultReport(score) {
    const showCertificateBtn = score >= 50
    ? `<button class="btn btn-outline-success btn-sm" id="view_certificate" onclick="displayCertificate(${current_course})">
           <i class="bi bi-award" id='giveCertificate'></i> View Certificate
       </button>`
    : ``

    const report = `
        <div class="score-section border rounded p-3 mb-3 mt-4 bg-light">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1 text-muted">Your Score:-</h6>
                    <h2 class="fw-bold ${score >= 50 ? 'text-success' : 'text-danger'} mb-0">
                        <span id="quiz_score">${Math.trunc(score)}</span>%
                    </h2>
                </div>

                <div class="text-end">
                    <span class="badge ${score >= 50 ? 'bg-success' : 'bg-danger'} mb-2 d-inline-block">
                        ${score >= 50 ? 'Passed' : 'Fails'}
                    </span><br>
                    ${showCertificateBtn}
                </div>
            </div>
        </div>
    `
    quiz_info_container.insertAdjacentHTML('beforeend', report)
}

// to get result data from server------------------------
function getResultData() {
    fetch('/showResult',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            courseId: current_course
        })
    }).then(e=>e.json())
    .then(data => {
        if (data) {
            // console.log(data['score'])
            showResultReport(data['score'])
        }
    })
}
getResultData()
// to open certificate page---------------------
function displayCertificate(course_id) {
    window.open(`/certificate/${course_id}`, '_blank')
}