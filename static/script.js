async function loadSchedule() {
    const resp = await fetch('/api/schedule');
    const schedule = await resp.json();

    const container = document.getElementById('schedule');
    container.innerHTML = '';

    for (const [date, times] of Object.entries(schedule)) {
        const dayDiv = document.createElement('div');
        dayDiv.innerHTML = `<strong>${date}:</strong> ${times.join(', ')}`;
        container.appendChild(dayDiv);
    }
}

loadSchedule();
