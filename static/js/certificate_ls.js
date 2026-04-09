// to create div to list certificate-----------------
function showMyCertificate(course_name,course_id) {
    const bar = `
    <div class="modern-card mb-3 d-flex flex-sm-row flex-column justify-content-between align-items-sm-center gap-3">
        <div class="d-flex align-items-center gap-3">
            <div class="bg-success bg-opacity-25 rounded p-3 text-success">
                <i class="bi bi-mortarboard fs-4"></i>
            </div>
            <div>
                <h6 class="text-secondary small text-uppercase fw-semibold mb-1">Certificate of Completion</h6>
                <h5 class="fw-bold mb-0 text-white">${course_name}</h5>
            </div>
        </div>
        <button class="btn btn-outline-premium px-4 text-nowrap" course_id="${course_id}" onclick="displayCertificate(this.getAttribute('course_id'))">
            <i class="bi bi-eye me-2"></i> View Certificate
        </button>
    </div>
    `
    document.getElementById('certificateList').insertAdjacentHTML('beforeend', bar);
}

// to get the list of certificate of that users--------------------
fetch('/getAllCertificate').then(e=>e.json())
.then(data => {
    const listContainer = document.getElementById('certificateList');
    if (data.length === 0) {
        listContainer.innerHTML = `
            <div class="text-center py-5 glass-panel">
                <i class="bi bi-award text-secondary opacity-50" style="font-size: 4rem;"></i>
                <h4 class="mt-3 text-secondary">No Certificates yet</h4>
                <p class="text-secondary small">Complete a course to earn your first certificate!</p>
                <a href="/home#showCourses" class="btn btn-premium mt-3">Explore Courses</a>
            </div>
        `
        return;
    }
    
    for (const i of data) {
        showMyCertificate(i.course_title,i.course_id)
    }
})
.catch(error => {
    console.error(error);
})


// to open certificate when view btn is clicked-----------------
function displayCertificate(course_id) {
    window.open(`/certificate/${course_id}`, '_blank');
}