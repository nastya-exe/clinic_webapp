window.onload = async function () {
    const urlParams = new URLSearchParams(window.location.search);
    const doctorId = urlParams.get("doctor_id");

    if (!doctorId) {
        alert("Не передан doctor_id в URL");
        return;
    }
    const patientId = urlParams.get("patient_id");

        if (!patientId) {
            alert("Не передан patient_id в URL");
            return;
        }


    // Получаем полное имя врача через API
    let doctorName = "";
    try {
        const nameResponse = await fetch(`/api/doctor_name?doctor_id=${doctorId}`);
        if (nameResponse.ok) {
            const data = await nameResponse.json();
            doctorName = data.full_name;
        } else {
            console.warn("Не удалось загрузить имя врача");
        }
    } catch (error) {
        console.error("Ошибка при загрузке имени врача:", error);
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

                    timeButton.onclick = async () => {
                        const appointmentDateTime = `${date}T${time}:00`;

                        try {
                            const response = await fetch("/api/book", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({
                                    doctor_id: parseInt(doctorId),
                                    appointment_time: appointmentDateTime,
                                    patient_id: parseInt(patientId)
                                })
                            });

                            if (!response.ok) {
                                const err = await response.json();
                                alert("Ошибка записи: " + err.detail);
                                return;
                            }

                            alert(`Вы записались к врачу ${doctorName || ''} на ${appointmentDateTime}`);
                        } catch (error) {
                            alert("Ошибка при попытке записи: " + error.message);
                        }
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
