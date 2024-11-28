const images = document.querySelectorAll('.zoom-image');

images.forEach(image => {
    // Додаємо подію при наведенні миші
    image.addEventListener('mouseenter', () => {
        image.style.transform = 'scale(1.03)'; // Зменшити приближення до 5%
    });

    // Додаємо подію при відведенні миші
    image.addEventListener('mouseleave', () => {
        image.style.transform = 'scale(1)'; // Відновлення до початкового розміру
    });

});
document.addEventListener('DOMContentLoaded', () => {
const track = document.querySelector('.carousel-track');
const images = document.querySelectorAll('.carousel-image');
let currentIndex = 0;

// Функція для зміщення зображень
function moveToNextSlide() {
    currentIndex++;
    if (currentIndex >= images.length - 3) { // Зменшено на 3, щоб показувати 4 фото
        currentIndex = 0; // Повернення до початку
    }
    const offset = currentIndex * -25; // Розрахунок зміщення
    track.style.transform = `translateX(${offset}%)`;
}

// Зміна зображення кожні 3 секунди
setInterval(moveToNextSlide, 3000); })


// Отримуємо всі кнопки "Додати в кошик"
const buttons = document.querySelectorAll('.add-to-cart-button');


$(document).ready(function () {
    // Обробка відправки форми через AJAX
    $('#order-form').on('submit', function (e) {
        e.preventDefault(); // Запобігаємо стандартній поведінці форми

        // Збираємо дані форми
        const formData = {
            name: $('#name').val(),
            email: $('#email').val(),
            address: $('#address').val()
        };

        $.ajax({
            url: '/checkout', // Ваш серверний маршрут
            method: 'POST', // Метод відправки
            data: formData, // Дані, що надсилаються
            success: function (response) {
                // Сховаємо форму
                $('#order-form').hide();

                // Виводимо повідомлення, яке повернув сервер
                $('#response-message')
                    .text('Дякуємо за замовлення!')
                    .show();
            },
            error: function () {
                // Вивести повідомлення про помилку
                $('#response-message')
                    .text('Сталася помилка. Спробуйте ще раз!')
                    .css('color', 'red')
                    .show();
            }
        });
    });

        // Очистимо поля форми
        $('#name').val('');
        $('#email').val('');
        $('#address').val('');
    });
