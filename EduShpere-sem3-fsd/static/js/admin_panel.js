// Navigation Logic
function showSection(sectionId, event) {
    if(event) event.preventDefault();
    ['dashboard','users','courses'].forEach(id=>{
        document.getElementById(id+'-section').style.display='none';
    });
    document.getElementById(sectionId+'-section').style.display='block';
    document.querySelectorAll('#sidebar .nav-link')
        .forEach(link => link.classList.remove('active'));

    if(event)
        event.currentTarget.classList.add('active');

    // Load data
    if(sectionId==='users') loadUsers();
    if(sectionId==='courses') loadCourses();
}


// Fetch Dashboard Data
document.addEventListener('DOMContentLoaded', function() {
    fetch('/admin/data')
        .then(response => response.json())
        .then(data => {
            // Populate Top Institutes Table
            const tbody = document.querySelector('#top-institutes-table tbody');
            if (data.top_institutes && data.top_institutes.length > 0) {
                tbody.innerHTML = data.top_institutes.map(i => 
                    `<tr><td>${i.name}</td><td>${i.course_count}</td><td>${i.enrollments}</td></tr>`
                ).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No data available.</td></tr>';
            }
        });
});

function loadUsers() {
    fetch('/admin/users')
        .then(res => res.json())
        .then(users => {

            const students = users.filter(u => u.role === 'Student');
            const institutes = users.filter(u => u.role === 'Institute');

            const renderRow = (user) => `
                <tr>
                    <td>${user.user_id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger"
                            onclick="deleteUser(${user.user_id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;

            const renderInstituteRow = (user) => `
                <tr>
                    <td>${user.user_id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1"
                            onclick="viewInstituteCourses(${user.user_id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger"
                            onclick="deleteUser(${user.user_id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;

            //Ensure table exists before writing
            const studentTable = document.querySelector('#students-table tbody');
            const instituteTable = document.querySelector('#institutes-table tbody');

            if(studentTable)
                studentTable.innerHTML = students.map(renderRow).join('');

            if(instituteTable)
                instituteTable.innerHTML = institutes.map(renderInstituteRow).join('');
        });
}


function loadCourses() {
    fetch('/admin/courses')
        .then(res => res.json())
        .then(courses => {
            const tbody = document.querySelector('#courses-table tbody');
            tbody.innerHTML = courses.map(course => `
                <tr>
                    <td>${course.course_id}</td>
                    <td>${course.course_title}</td>
                    <td>₹${course.course_price}</td>
                    <td>${course.owner_name || 'Unknown'}</td>
                </tr>
            `).join('');
        });
}

function deleteUser(id) {
    if(confirm('Are you sure you want to delete this user?')) {
        fetch('/admin/delete_user', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: id})
        })
        .then(res => res.json().then(data => {
            if(data.message === 'Deleted') loadUsers(); else alert('Failed to delete user.');
        }));
    }
}

function filterTable(tableId, query) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    const rows = tbody.getElementsByTagName('tr');
    query = query.toLowerCase();

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    }
}

function viewInstituteCourses(userId) {
    fetch(`/admin/institute_courses/${userId}`)
        .then(res => res.json())
        .then(courses => {
            const tbody = document.querySelector('#modal-courses-table tbody');
            if (courses.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center">No courses found.</td></tr>';
            } else {
                tbody.innerHTML = courses.map(c => `
                    <tr><td>${c.course_id}</td><td>${c.course_title}</td><td>₹${c.course_price}</td></tr>
                `).join('');
            }
            new bootstrap.Modal(document.getElementById('coursesModal')).show();
        });
}
