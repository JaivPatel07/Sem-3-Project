// to create div to list certificate-----------------
function showMyCertificate(course_name,course_id) {
    const bar = `
    <div class="certificate-card d-flex justify-content-between align-items-center">
        <div class="course-name">${course_name}</div>
        <button class="btn btn-sm btn-outline-primary px-4" course_id="${course_id}" onclick="displayCertificate(this.getAttribute('course_id'))">View</button>
    </div>
    `
    document.getElementById('certificateList').insertAdjacentHTML('beforeend', bar);
}

// to get the list of certificate of that users--------------------
fetch('/getAllCertificate').then(e=>e.json())
.then(data => {
    console.log(data)
    for (const i of data) {
        showMyCertificate(i.course_title,i.course_id)
    }
})
.catch(error => console.error(error))


// to open certificate when view btn is clicked-----------------
function displayCertificate(course_id) {
    window.open(`/certificate/${course_id}`, '_blank');
}