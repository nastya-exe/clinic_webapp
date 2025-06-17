window.onload = async function() {
    const urlParams = new URLSearchParams(window.location.search);
    const doctorId = urlParams.get("doctor_id");
    let doctorName = urlParams.get("doctor_name");
    if (doctorName) doctorName = decodeURIComponent(doctorName);

    if (!doctorId) {
        alert("Не передан doctor_id в URL");
        return;
    }

    // Показать имя врача
    const doctorNameDiv = document.getElementById('doctor-name');
    doctorNameDiv.textContent = doctorName ? `Расписание врача: ${doctorName}` : "Расписание врача";

    try {
        const response = await fetch(`/api/schedule?doctor_id=${doctorId}`);
        if (!response.ok) throw new Error(`Ошибка при загрузке расписания: ${response.status}`);

        const schedule = await response.json();

        const datesContainer = document.getElementById('dates');
        const timesContainer = document.getElementById('times');

        datesContainer.innerHTML = '';
        timesContainer.innerHTML = '';

        if (Object.keys(schedule).length === 0) {
            datesContainer.textContent = "Нет доступных дат.";
            return;
        }

        for (const [date, times] of Object.entries(schedule)) {
            const dateButton = document.createElement('button');
            dateButton.textContent = date;
            dateButton.className = 'date-button';

            dateButton.onclick = () => {
                timesContainer.innerHTML = '';
                times.forEach(time => {
                    const timeButton = document.createElement('button');
                    timeButton.textContent = time;
                    timeButton.className = 'time-button';

                    timeButton.onclick = () => {
                        alert(`Вы записались к врачу ${doctorName || ''} на ${date} в ${time}`);
                        // TODO: здесь можно добавить вызов API для записи или переход в бота
                    };

                    timesContainer.appendChild(timeButton);
                });
            };

            datesContainer.appendChild(dateButton);
        }

    } catch (error) {
        console.error("Ошибка при получении расписания:", error);
        const datesContainer = document.getElementById('dates');
        datesContainer.textContent = "Не удалось загрузить расписание.";
    }
};
