const courseNames = []
const enrollments = {}
const scores = {}

fetch('/getResultForInstituate')
  .then(res => res.json())
  .then(data => {

    if (!data || data.length === 0) {
        console.log('no data found')
        return
    }

    // ---------- Collect ----------
    for (const row of data) {
        const courseTitle = row.course_title
        const score = row.score ?? 0

        if (!courseNames.includes(courseTitle)) {
            courseNames.push(courseTitle)
        }

        enrollments[courseTitle] = (enrollments[courseTitle] || 0) + 1
        scores[courseTitle] = (scores[courseTitle] || 0) + score
    }

    // ---------- Prepare Arrays ----------
    const total_enrolled = []
    const avg_scores = []

    let total_score_sum = 0
    let total_students = 0

    for (const course of courseNames) {
        total_enrolled.push(enrollments[course])

        total_score_sum += scores[course]
        total_students += enrollments[course]

        avg_scores.push((scores[course] / enrollments[course]).toFixed(2))
    }

    const avg = (total_score_sum / total_students).toFixed(2)

    // ---------- Highest Course ----------
    let highname = ''
    let highmark = 0

    for (const course of courseNames) {
        if (scores[course] > highmark) {
            highmark = scores[course]
            highname = course
        }
    }

    document.getElementById('highcourse').innerText = highname
    document.getElementById('highper').innerText = highmark.toFixed(2)
    document.getElementById('avgscore').innerText = avg

    // ---------- Charts ----------
    new Chart(document.getElementById('enrollmentChart'), {
        type: 'bar',
        data: {
            labels: courseNames,
            datasets: [{
                label: 'Students Enrolled',
                data: total_enrolled
            }]
        }
    })

    new Chart(document.getElementById('scoreChart'), {
        type: 'bar',
        data: {
            labels: courseNames,
            datasets: [{
                label: 'Average Score (%)',
                data: avg_scores
            }]
        }
    })
})
