const course_title = document.getElementById('course-title')
const course_chapters_name = document.querySelector('#course-chapters')
const teaching_part = document.querySelector('.video-container')
const video_title = document.querySelector('#video-title')
const video_url = document.querySelector('iframe')

const chapter_overview = document.querySelector('#overview p')
const chapter_notes = document.querySelector('#notes_url')
const markCompleteBtn = document.querySelector('#markCompleteBtn')


// to display list of chapters in that courses------------
function add_courses_name(name_list) {
    for (const name of name_list) {
        let btns = `
        <button class="list-group-item list-group-item-secondary text-start mb-2 p-2 rounded" chapter_id=${name[0]}>${name[1]}</button>
        `
        course_chapters_name.insertAdjacentHTML('beforeEnd',btns)
    }
}

// to handle all data of that module-----------------
let module_data = []

// to fetch data of the current module------------------------
const current_course = course_title.getAttribute('current_course_id')


fetch(`/courseData/${current_course}`).then(e=>e.json())
.then(data => {
    course_title.innerText = data[data.length-1]
    let chapters_name = []

    for (let index = 0; index < data.length-1; index++) {
        element = data[index]
        chapters_name.push([element.chapter_id,element.chapter_title])
        module_data.push(element)
    }
    add_courses_name(chapters_name)
})



course_chapters_name.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        
        const chapter_id = e.target.getAttribute('chapter_id')
        let chapter_data = []
        
        for (const element of module_data) {
            if (element.chapter_id===parseInt(chapter_id)) {
                chapter_data.push(element)
                break
            }
        }
        
        video_title.innerHTML = chapter_data[0]['chapter_title']
        const videoId = chapter_data[0]['chapter_video'].split('&')[0]
        video_url.src = `https://www.youtube.com/embed/${videoId}`
        chapter_overview.innerText = chapter_data[0]['chapter_description']
        chapter_notes.innerText = chapter_data[0]['chapter_notes']
        markCompleteBtn.setAttribute('chapter_id',chapter_data[0]['chapter_id'])
        // to make teaching pary visible only when chapter is selected----------
        teaching_part.style.visibility = 'visible'
    }
});


function markComplete(btn) {
    chapter_id = btn.getAttribute('chapter_id')
    fetch("/chapterComplete", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            courseId: current_course,
            chapterId: chapter_id
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message)
    })
    .catch(err => console.error(err))
}



// for quiz part--------------------------------------------------------

// to hide teaching_part and show quiz part----------
function showQuizDetails() {
    teaching_part.classList.add('d-none')
    quiz_info_container.classList.remove('d-none')
}


const quiz_info_container = document.querySelector('.quiz-info-container')
const next_btn = document.getElementById('next_btn')
const question_borad = document.querySelector('.modal-body')
const start_btn = document.querySelector('#start_quiz')

// to make question------------
function loadQuestion(question,opta,optb,optc,optd) {
    const quiz_question = `
    <div class="quiz-form">
        <strong class="mb-2">Que. <span> ${question}</span></strong>

        <div id="quiz_options">
            <div><input type="radio" name="quiz_option" class="form-check-input" value="A"> <span>${opta}</span></div>
            <div><input type="radio" name="quiz_option" class="form-check-input" value="B"> <span>${optb}</span></div>
            <div><input type="radio" name="quiz_option" class="form-check-input" value="C"> <span>${optc}</span></div>
            <div><input type="radio" name="quiz_option" class="form-check-input" value="D"> <span>${optd}</span></div>
        </div>
    
    </div>
    `
    question_borad.insertAdjacentHTML('beforeend',quiz_question)
}

// to get quiz data ------------------------------

// to start timer timer----------
let totalTime = 1 * 60; // 5 minutes (in seconds)
let timerInterval = null;

// ready is used to know that it is allowed to start timer or not
function startQuizTimer(data,data_len,ready) {
    const timerEl = document.getElementById("timer");

    timerInterval = setInterval(() => {
        let minutes = Math.floor(totalTime / 60);
        let seconds = totalTime % 60;

        timerEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        if (totalTime <= 0 || !ready) {
            clearInterval(timerInterval);
            timerEl.textContent = "00:00";
            calculateScore(data,data_len)
            closeQuizModal()
            return
        }
        totalTime--;
    }, 1000);
}

// to close modal box when time gets over-------------
function closeQuizModal() {
    const modalEl = document.getElementById('quiz_box');
    const modal = bootstrap.Modal.getInstance(modalEl);

    if (modal) {
        modal.hide();
    }
}


// to calculate score of quiz-----------------------
function calculateScore(data,data_len) {
    let right = 0;

    for (let index = 0; index < user_answer.length; index++) {
        if (user_answer[index] === real_answer[index]) {
            right++
        }
    }

    let score = (right / data_len) * 100
    if (!data[data_len].isAttempt || pos <= data_len-1) {
        // to submit quiz score------------
        quizFinished(score)
        start_btn.innerText = 'Attempt Finished!'
    }
    else {
        alert('you can submit only one time!!!')
    }
}


// to send result of the quiz-----------------
function quizFinished(result) {
    fetch('/quizFinished',{
        method:'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            courseId: current_course,
            score: result
        })
    }).then(e=>e.json())
    .catch(error => console.error(error))
}



let pos = 0
const user_answer = []
const real_answer = []

// to show particular question------------
function showQuestion(data) {
    let data_len = data.length - 1
    const q = data[pos];
    loadQuestion(q.question_text,q.optiona,q.optionb,q.optionc,q.optiond)

    if (pos === data_len - 1) {
        next_btn.innerText = 'Submit'
        next_btn.setAttribute('data-bs-dismiss', 'modal')
    } else {
        next_btn.innerText = 'Next'
    }
}

// main part to load question and quiz part------------------
fetch('/moduleQuiz', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        courseId: current_course
    })
})
.then(res => res.json())
.then(data => {

    let data_len = data.length - 1

    if (data[data_len].isAttempt) {
        start_btn.innerText = 'Attempt Finished!'
        next_btn.innerText = 'close'
        next_btn.setAttribute('data-bs-dismiss', 'modal')
        question_borad.innerHTML = '<h5 style="color:red;">You Already Attempt Quiz!!!</h5>'
        document.getElementById('quiz_attempts').innerText = 0
        startQuizTimer(data,data_len,false)
        is_Attempt = true

        // to show result report data--------------------
        getResultData()
        return; 
    }

    // to get real_answer of all the questions--------------------
    for (let pos = 0; pos < data.length-1; pos++) {
        real_answer.push(data[pos].answer)
    }
    // console.log(real_answer)

    start_btn.addEventListener('click',() => {
        startQuizTimer(data,data_len,true) // to start quiz timer when start btn is clicked
    })

    // to show first question data----------------
    showQuestion(data);

    // to get user selected option to user_answer---------
    question_borad.addEventListener('change', (e) => {
        if (e.target.name === 'quiz_option') {
            user_answer[pos] = e.target.value; // 🔥 store by question index
        }
    });

    
    next_btn.addEventListener('click', () => {
        const selected = document.querySelector('input[name="quiz_option"]:checked')
        if (!selected) {
            alert('please select option!!!')
            return
        }
        else {
            pos++
        }
        if (pos < data_len) { // if pos > data_len it means that all the question is printed
            question_borad.innerHTML = ''
            showQuestion(data);
        } else {
            calculateScore(data,data_len)
        }
    });
})
.catch(err => console.error(err))


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
        // console.log(data['score'])
        showResultReport(data['score'])
    })
}

// to open certificate page---------------------
function displayCertificate(course_id) {
    window.open(`/certificate/${course_id}`, '_blank');
}