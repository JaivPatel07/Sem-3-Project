const module_submit = document.getElementById('module_submit')


// to store question when addQuestion click----------
let questions_list = []

// to store the questions when sumbit button is clicked-------------
let final_question_list = []

const addQuestion = document.getElementById('addNewQuestion')
const saveQuestion = document.getElementById('submitQuestion')

// to save questions data------------------
addQuestion.addEventListener('click', () => {
    const que = document.getElementById('que')
    const op1 = document.getElementById('op1')
    const op2 = document.getElementById('op2')
    const op3 = document.getElementById('op3')
    const op4 = document.getElementById('op4')
    const ans = document.getElementById('ans')

    // Trim values to avoid spaces
    const questionText = que.value.trim()
    const option1 = op1.value.trim()
    const option2 = op2.value.trim()
    const option3 = op3.value.trim()
    const option4 = op4.value.trim()
    const answer = ans.value.trim().toUpperCase()

    // Empty field validation
    if (!questionText || !option1 || !option2 || !option3 || !option4 || !answer) {
        alert("All fields are required!")
        return
    }

    // Answer validation
    if (!["A", "B", "C", "D"].includes(answer)) {
        alert("Answer must be A, B, C or D")
        return
    }

    // Create question object
    const question = {
        question: questionText,
        option1: option1,
        option2: option2,
        option3: option3,
        option4: option4,
        answer: answer
    }
    questions_list.push(question)
    // Clear inputs
    que.value = ""
    op1.value = ""
    op2.value = ""
    op3.value = ""
    op4.value = ""
    ans.value = ""
})

saveQuestion.addEventListener('click',()=> {
    final_question_list = questions_list
    questions_list = []
})


const addChapter = document.getElementById('addNewChapter')
const chapter_data_list = []

// to add chapters data -------------------------
addChapter.addEventListener('click', () => {
    console.log('hello')
    const title = document.getElementById('chapter_title')
    const yt_url = document.getElementById('yt_url')
    const notes_url = document.getElementById('notes_url')
    const des = document.getElementById('chapter_des')

    const chapterTitle = title.value.trim()
    const youtubeURL = yt_url.value.trim()
    const notesURL = notes_url.value.trim()
    const description = des.value.trim()

    

    // Empty field validation
    if (!chapterTitle || !youtubeURL || !notesURL || !description) {
        alert("All fields are required!")
        return
    }

    const chapter = {
        title: chapterTitle,
        yt_url: youtubeURL,
        notes_url: notesURL,
        description: description,
        
    }

    chapter_data_list.push(chapter)

    title.value = ""
    yt_url.value = ""
    notes_url.value = ""
    des.value = ""
    final_question_list = []

    // console.log(chapter.questions)
})

let module_data = {}

// to get data when module is sumbit----------
module_submit.addEventListener('click',() => {

    // for module part of page-----------------------------------------------------------------------
    const module_title = document.getElementById('module_title').value.trim()
    const module_des = document.getElementById('module_des').value.trim()
    const module_price = document.getElementById('module_price').value.trim()
    const module_cat = document.getElementById('module_cat').value.trim()

    if (!module_title || !module_des || !module_price || !module_cat) {
        alert('None Field Should be empty!!!')
        return
    }

    if (isNaN(module_price)) {
        alert('Price must be in number!!!')
        return
    }
    if (chapter_data_list.length==0) {
        alert('Please save chapter first Or Add Chapter!!!')
        // return
    }
    if (final_question_list.length<2) {
        alert('Please Enter Atleast 5 Questions!!!')
        return
    }

    module_data = {
        module_title:module_title,
        module_des:module_des,
        module_price:module_price,
        module_cat:module_cat,
        module_chapters: chapter_data_list,
        module_question: final_question_list
    }
    // console.log(module_data)

    fetch('/publishCourse',{
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(module_data)
    }).then(res => res.json())
    .then(data => {
        alert(data.message)
    })
    .catch(error => {
        alert(error)
    })
})