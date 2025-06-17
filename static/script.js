window.onload = async function loadSchedule() {
    const doctorId = 7;  // ВРЕМЕННАЯ ЗАТЫЧКА!

    try {
        const response = await fetch(`/api/schedule?doctor_id=${doctorId}`);
        if (!response.ok) throw new Error("Ошибка при загрузке расписания");

        const schedule = await response.json();
        // здесь остальной код для отрисовки слотов
        console.log(schedule); // для проверки
    } catch (error) {
        console.error("Ошибка при получении расписания:", error);
    }
}

        if (!response.ok) {
            throw new Error(`Ошибка при загрузке расписания: ${response.status}`);
        }

        const schedule = await response.json();

        const datesContainer = document.getElementById('dates');
        const timesContainer = document.getElementById('times');

        // Очистим контейнеры, если вдруг страница не перезагружается
        datesContainer.innerHTML = '';
        timesContainer.innerHTML = '';

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
                        // TODO: сюда добавить POST-запрос на бронирование
                    };

                    timesContainer.appendChild(timeButton);
                });
            };

            datesContainer.appendChild(dateButton);
        }

        if (Object.keys(schedule).length === 0) {
            datesContainer.textContent = "Нет доступных дат.";
        }

    } catch (error) {
        console.error("Ошибка при получении расписания:", error);
        const datesContainer = document.getElementById('dates');
        datesContainer.textContent = "Не удалось загрузить расписание.";
    }
};
