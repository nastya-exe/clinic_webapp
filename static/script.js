// static/script.js

async function loadSchedule() {
    const response = await fetch('/api/schedule');
    const schedule = await response.json();

    const datesContainer = document.getElementById('dates');
    const timesContainer = document.getElementById('times');

    for (const [date, times] of Object.entries(schedule)) {
        const btn = document.createElement('button');
        btn.textContent = date;
        btn.className = 'date-button';
        btn.onclick = () => {
            // Очищаем старые кнопки времени
            timesContainer.innerHTML = '';
            times.forEach(time => {
                const timeBtn = document.createElement('button');
                timeBtn.textContent = time;
                timeBtn.className = 'time-button';
                timeBtn.onclick = () => {
                    alert(`Вы записались на ${date} в ${time}`);
                    // Тут позже будет POST-запрос на сервер
                };
                timesContainer.appendChild(timeBtn);
            });
        };
        datesContainer.appendChild(btn);
    }
}

window.onload = loadSchedule;
