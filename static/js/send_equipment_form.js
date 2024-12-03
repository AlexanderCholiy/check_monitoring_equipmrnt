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
    if (controllerNumber || cabinetNumber) {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}