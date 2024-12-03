function toggleInputs(supportCodeInput) {
    const isFilled = supportCodeInput.value.trim() !== '';
    const dependentInputs = document.querySelectorAll('#controller-number, #cabinet-number');
    dependentInputs.forEach(input => {
        input.disabled = isFilled;
        if (isFilled) {
            input.value = ''; // Очищаем зависимые поля
        }
    });
    validateForm();
}

function validateForm() {
    const controllerNumber = document.getElementById('controller-number').value.trim();
    const cabinetNumber = document.getElementById('cabinet-number').value.trim();
    const submitButton = document.getElementById('submit-button');
    
    // Разблокируем кнопку, если хотя бы одно из полей заполнено
    submitButton.disabled = !(controllerNumber || cabinetNumber);
}

function validateRequiredFields() {
    const controllerNumber = document.getElementById('controller-number').value.trim();
    const cabinetNumber = document.getElementById('cabinet-number').value.trim();

    if (!controllerNumber && !cabinetNumber) {
        // Подсказка для пользователя
        alert("Пожалуйста, заполните хотя бы одно из полей: 'Номер контроллера' или 'Номер шкафа'.");
        
        // Подсветка полей, если ни одно не заполнено
        document.getElementById('controller-number').classList.add('error');
        document.getElementById('cabinet-number').classList.add('error');
        return false; // Блокируем отправку формы
    }

    // Убираем подсветку, если хотя бы одно поле заполнено
    document.getElementById('controller-number').classList.remove('error');
    document.getElementById('cabinet-number').classList.remove('error');
    return true; // Разрешаем отправку формы
}

