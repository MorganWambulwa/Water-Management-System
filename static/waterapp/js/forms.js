document.addEventListener('DOMContentLoaded', function () {
    const numberInputs = document.querySelectorAll('input[type="number"].no-spinners');
    numberInputs.forEach(input => {
        input.addEventListener('keydown', (event) => {
            if (event.key === '-' || event.key === 'e') {
                event.preventDefault();
            }
        });
    });
});
