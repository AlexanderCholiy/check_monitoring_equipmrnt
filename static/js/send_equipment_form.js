function validateRequiredFields() {
    const cabinetInput = document.getElementById('cabinet-number');
    const controllerInput = document.getElementById('controller-number');
    const firstcounternumberInput = document.getElementById('counter-number-1');
    
    const cabinetNumber = cabinetInput.value.trim();
    const controllerNumber = controllerInput.value.trim();
    const firstcounternumber = firstcounternumberInput.value.trim();
    
    let isValid = true;

    // Убираем классы ошибок
    cabinetInput.classList.remove('error');
    controllerInput.classList.remove('error');
    firstcounternumberInput.classList.remove('error');

    // Проверяем, заполнены ли оба поля
    if (!cabinetNumber && !controllerNumber && !firstcounternumber) {
        alert('Пожалуйста, введите номер шкафа или номер контроллера или номер счётчика.');
        isValid = false; // предотвращает отправку формы
        
        // Добавляем классы ошибок
        cabinetInput.classList.add('error');
        controllerInput.classList.add('error');
        firstcounternumberInput.classList.add('error');
    }

    return isValid; // возвращаем результат валидации
}

function clearError(input) {
    input.classList.remove('error'); // Убираем класс ошибки при вводе данных
}