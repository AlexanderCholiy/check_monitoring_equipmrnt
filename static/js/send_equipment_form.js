function validateRequiredFields() {
    const cabinetInput = document.getElementById('cabinet-number');
    const controllerInput = document.getElementById('controller-number');
    
    const cabinetNumber = cabinetInput.value.trim();
    const controllerNumber = controllerInput.value.trim();
    
    let isValid = true;

    // Убираем классы ошибок
    cabinetInput.classList.remove('error');
    controllerInput.classList.remove('error');

    if (!cabinetNumber && !controllerNumber) {
        alert('Пожалуйста, введите номер шкафа или номер контроллера.');
        isValid = false; // предотвращает отправку формы
        
        // Добавляем классы ошибок
        cabinetInput.classList.add('error');
        controllerInput.classList.add('error');
    }

    return isValid; // возвращаем результат валидации
}

function clearError(input) {
    input.classList.remove('error'); // Убираем класс ошибки при вводе данных
}