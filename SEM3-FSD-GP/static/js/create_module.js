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
    final_question_list = final_question_list.concat(questions_list)
    questions_list = []
    renderQuestionStack()
    info_msg('Questions saved to module successfully', 'success')
})

function info_msg(msg, color = 'info') {
    const mssg = `
        <div class="alert alert-${color} alert-dismissible position-absolute mt-5 start-50 translate-middle fade show w-50"
             style="z-index:1055;">
            ${msg}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.insertAdjacentHTML('afterbegin', mssg);

    // to remove error after 1second-------------
    setTimeout(() => {
        const alertEl = document.querySelector('.alert');
        if (alertEl) {
            bootstrap.Alert.getOrCreateInstance(alertEl).close();
        }
    }, 1000);
}


const addChapter = document.getElementById('addNewChapter')
const chapter_data_list = []

// to add chapters data -------------------------
addChapter.addEventListener('click', () => {
    const title = document.getElementById('chapter_title')
    const yt_url = document.getElementById('yt_url')
    const notes_url = document.getElementById('notes_url')
    const des = document.getElementById('chapter_des')

    const chapterTitle = title.value.trim()
    const youtubeURL = yt_url.value.trim()
    const notesURL = notes_url.value.trim()
    const description = des.value.trim()

    if (!chapterTitle || !youtubeURL || !notesURL || !description) {
        info_msg("All fields are required!",'danger')
        return
    }
    const chapter = {
        title: chapterTitle,
        yt_url: youtubeURL,
        notes_url: notesURL,
        description: description
    }

    chapter_data_list.push(chapter)
    renderChapterStack()
    info_msg('Chapter Added to Stack Successfully', 'success')
    title.value = ""
    yt_url.value = ""
    notes_url.value = ""
    des.value = ""
    final_question_list = []

    // console.log(chapter.questions)
})

// Function to render the chapter stack visually
function renderChapterStack() {
    const stackContainer = document.getElementById('chapter_stack_container');
    const stackList = document.getElementById('chapter_stack_list');
    
    if (!stackContainer || !stackList) return;

    if (chapter_data_list.length > 0) {
        stackContainer.classList.remove('d-none');
    } else {
        stackContainer.classList.add('d-none');
    }

    stackList.innerHTML = '';

    // Display in reverse order to simulate a Stack (LIFO - Last In First Out)
    [...chapter_data_list].reverse().forEach((chapter, index) => {
        const realIndex = chapter_data_list.length - 1 - index;
        const item = `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center animate__animated animate__fadeIn">
                <div>
                    <h6 class="mb-1 fw-bold"><i class="bi bi-layers-fill text-primary me-2"></i>${chapter.title}</h6>
                    <small class="text-muted">${chapter.description.substring(0, 40)}${chapter.description.length > 40 ? '...' : ''}</small>
                </div>
                <div>
                    <button class="btn btn-outline-primary btn-sm me-2" onclick="editChapterFromStack(${realIndex})">
                        <i class="bi bi-pencil-square"></i> Edit
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="removeChapterFromStack(${realIndex})">
                        <i class="bi bi-trash"></i> Remove
                    </button>
                </div>
            </div>
        `;
        stackList.insertAdjacentHTML('beforeend', item);
    });
}
// Global function to remove chapter from stack
let chapterIndexToRemove = null;

window.removeChapterFromStack = function(index) {
    chapterIndexToRemove = index;
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmRemoveModal'));
    confirmModal.show();
};

// confirm removal button event listener
document.getElementById('confirmRemoveBtn').addEventListener('click', () => {
    if (chapterIndexToRemove !== null) {
        chapter_data_list.splice(chapterIndexToRemove, 1);
        renderChapterStack();
        info_msg('Chapter removed from stack', 'warning');
        const confirmModalEl = document.getElementById('confirmRemoveModal');
        const modalInstance = bootstrap.Modal.getInstance(confirmModalEl);
        modalInstance.hide();
        chapterIndexToRemove = null;
    }
});

// Global function to edit chapter from stack
window.editChapterFromStack = function(index) {
    const chapter = chapter_data_list[index];
    document.getElementById('chapter_title').value = chapter.title;
    document.getElementById('yt_url').value = chapter.yt_url;
    document.getElementById('notes_url').value = chapter.notes_url;
    document.getElementById('chapter_des').value = chapter.description;
    // Remove from stack so it can be re-added
    chapter_data_list.splice(index, 1);
    renderChapterStack();
    info_msg('Chapter loaded for editing. Click "Save Chapter" to update.', 'info');
}

// Function to render the Question stack visually
function renderQuestionStack() {
    const stackContainer = document.getElementById('question_stack_container');
    const stackList = document.getElementById('question_stack_list');
    
    if (!stackContainer || !stackList) return;

    if (final_question_list.length > 0) {
        stackContainer.classList.remove('d-none');
    } else {
        stackContainer.classList.add('d-none');
    }
    stackList.innerHTML = '';
    [...final_question_list].reverse().forEach((q, index) => {
        const realIndex = final_question_list.length - 1 - index;
        const item = `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center animate__animated animate__fadeIn">
                <div>
                    <h6 class="mb-1 fw-bold"><i class="bi bi-question-circle-fill text-info me-2"></i>${q.question}</h6>
                    <small class="text-muted">Ans: <span class="badge bg-success">${q.answer}</span></small>
                </div>
                <div>
                    <button class="btn btn-outline-primary btn-sm me-2" onclick="editQuestionFromStack(${realIndex})">
                        <i class="bi bi-pencil-square"></i> Edit
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="removeQuestionFromStack(${realIndex})">
                        <i class="bi bi-trash"></i> Remove
                    </button>
                </div>
            </div>
        `;
        stackList.insertAdjacentHTML('beforeend', item);
    });
}
window.removeQuestionFromStack = function(index) {
    final_question_list.splice(index, 1);
    renderQuestionStack();
    info_msg('Question removed from stack', 'warning');
}

window.editQuestionFromStack = function(index) {
    const question = final_question_list[index];

    // Populate form fields
    document.getElementById('que').value = question.question;
    document.getElementById('op1').value = question.option1;
    document.getElementById('op2').value = question.option2;
    document.getElementById('op3').value = question.option3;
    document.getElementById('op4').value = question.option4;
    document.getElementById('ans').value = question.answer;

    final_question_list.splice(index, 1);
    renderQuestionStack();

    const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('addQuestion'));
    modal.show();
    info_msg('Question loaded for editing.', 'info');
    console.log(question)
}

let module_data = {}

// to get data when module is submit----------
module_submit.addEventListener('click',() => {

    // for module part of page-----------------------------------------------------------------------
    const module_title = document.getElementById('module_title').value.trim()
    const module_des = document.getElementById('module_des').value.trim()
    const module_price = document.getElementById('module_price').value.trim()
    const module_cat = document.getElementById('module_cat').value.trim()

    if (!module_title || !module_des || !module_price || !module_cat) {
        info_msg('None Field Should be empty!!!','danger')
        return
    }

    if (isNaN(module_price)) {
        info_msg('Price must be in number!!!','danger')
        return
    }
    if (chapter_data_list.length==0) {
        info_msg('Please save chapter first Or Add Chapter!!!','danger')
    }
    if (final_question_list.length<5) {
        info_msg('Please Enter Atleast 5 Questions!!!','danger')
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
        info_msg(data.message,'success')
    })
    .catch(error => {
        info_msg(error,'danger')
    })

    
})

// Real-time preview updates for Module Info in Sidebar
const moduleTitleInput = document.getElementById('module_title');
const moduleDescInput = document.getElementById('module_des');
const modulePriceInput = document.getElementById('module_price');
const moduleCatInput = document.getElementById('module_cat');

const previewTitle = document.getElementById('preview_title');
const previewDesc = document.getElementById('preview_desc');
const previewPrice = document.getElementById('preview_price');
const previewCat = document.getElementById('preview_cat');

function updatePreview() {
    if (previewTitle) previewTitle.textContent = moduleTitleInput.value || 'Untitled Module';
    
    if (previewDesc) {
        const desc = moduleDescInput.value;
        // Limit description length in preview
        previewDesc.textContent = desc ? (desc.length > 60 ? desc.substring(0, 60) + '...' : desc) : 'No description added.';
    }
    if (previewPrice) {
        previewPrice.textContent = modulePriceInput.value ? `₹${modulePriceInput.value}` : '';
    }
    
    if (previewCat) {
        const selectedText = moduleCatInput.options[moduleCatInput.selectedIndex].text;
        previewCat.textContent = selectedText !== 'Select Category' ? selectedText : 'Category';
    }
}

// Logic to show Course Content only after Module Details are filled
const saveModuleDetailsBtn = document.getElementById('save_module_details_btn');
const courseContentCard = document.getElementById('course_content_card');

if (saveModuleDetailsBtn) {
    saveModuleDetailsBtn.addEventListener('click', () => {
        const module_title = document.getElementById('module_title').value.trim();
        const module_des = document.getElementById('module_des').value.trim();
        const module_price = document.getElementById('module_price').value.trim();
        const module_cat = document.getElementById('module_cat').value;

        if (!module_title || !module_des || !module_price || !module_cat || module_cat === '0') {
            info_msg('Please fill all Module Details fields correctly to proceed!', 'warning');
            return;
        }

        if (courseContentCard) {
            updatePreview();
            
            const moduleDetailsCard = document.getElementById('module_details_card');
            if (moduleDetailsCard) {
                moduleDetailsCard.classList.add('d-none');
            }

            courseContentCard.classList.remove('d-none');
            info_msg('Module Details saved. You can now add chapters.', 'success');
        }
    });
}

// Logic to Edit Module Details (Show Module Details Card again)
const editModuleDetailsBtn = document.getElementById('edit_module_details_btn');
if (editModuleDetailsBtn) {
    editModuleDetailsBtn.addEventListener('click', () => {
        const moduleDetailsCard = document.getElementById('module_details_card');
        const courseContentCard = document.getElementById('course_content_card');
        
        if (moduleDetailsCard) moduleDetailsCard.classList.remove('d-none');
        if (courseContentCard) courseContentCard.classList.add('d-none');
    });
}
