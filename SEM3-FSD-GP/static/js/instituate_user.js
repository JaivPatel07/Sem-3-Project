function addUserList(user_name,user_email,user_course,join_date) {
    const code = `
    <tr>
        <td>
            <div class="d-flex align-items-center gap-3">
                <img src="https://placehold.co/100x100/png?text=${user_name[0].toUpperCase()}" class="avatar">
                <span class="fw-medium"  style="text-transform: capitalize;">${user_name}</span>
            </div>
        </td>
        <td>${user_email}</td>
        <td><span class="badge badge-course">${user_course}</span></td>
        <td>${join_date}</td>
        <td><span class="badge bg-success">Active</span></td>
    </tr>
    `
    document.getElementById('user_data_table').insertAdjacentHTML('beforeend',code)
}

const instituate_courses_ls = document.getElementById('instituate_courses')
// to get all the course data---------
// to add instituate course list to the page-------
fetch('/instituatesCourses').then(e => e.json())
.then(data => {
    for (const element of data) {
        const divv = document.createElement('option')
        divv.innerText = element.course_title
        instituate_courses_ls.appendChild(divv)
    }
    // to add count of and courses------
    document.getElementById('instituate_courses_count').innerText = data.length
})



// to get count of all the student----------
fetch('/GeneralData').then(e => e.json())
.then(data => {
    document.getElementById('all_student_count').innerText = data.length
})



// to store all the student data-------------
function renderStudent(search=null) {
    fetch('/instituateStudentData').then(e => e.json())
    .then(data => {
        document.getElementById('instituate_student').innerText = data.length
        for (const element of data) {
            if (search && search==='All Courses') {
                addUserList(element.name,element.email,element.course_title,element.join_date)
            }
            if (search) {
                if (element.course_title == search) {
                    addUserList(element.name,element.email,element.course_title,element.join_date)
                }
            }
            else {
                addUserList(element.name,element.email,element.course_title,element.join_date)
            }
        }
    })
    .catch(err => console.error(err))
}
renderStudent()


const student_data_ls = document.getElementById('students_data')
instituate_courses_ls.addEventListener('change',() => {
    // to clear previous data-------
    document.getElementById('user_data_table').innerHTML = ''
    renderStudent(instituate_courses_ls.value)
})

