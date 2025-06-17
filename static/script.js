window.onload = async function loadSchedule() {
    // Получаем doctor_id из параметров URL
    const urlParams = new URLSearchParams(window.location.search);
    const doctorId = urlParams.get('doctor_id');

    if (!doctorId) {
        const datesContainer = document.getElementById('dates');
        datesContainer.textContent = "Врач не выбран. Пожалуйста, выберите врача в боте и перейдите по ссылке.";
        return;
    }

    try {
        const response = await fetch(`/api/schedule?doctor_id=${doctorId}`);
        if (!response.ok) throw new Error(`Ошибка при загрузке расписания: ${response.status}`);

        const schedule = await response.json();

        const datesContainer = document.getElementById('dates');
        const timesContainer = document.getElementById('times');

        // Очистим контейнеры
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
                        alert(`Вы записались на ${date} в ${time}`);
                        // TODO: добавить POST-запрос на бронирование
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
