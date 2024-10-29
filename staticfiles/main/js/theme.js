const body = document.body;
const toggleSwitch = document.querySelector('#themeToggle');

function setThemeFromLocalStorage() {
    const savedTheme = localStorage.getItem('theme');
    const isDarkMode = localStorage.getItem('isDarkMode') === 'false';

    if (savedTheme) {
        body.classList.add(savedTheme);
        toggleSwitch.checked = isDarkMode;
    } else {

        body.classList.add('light-mode-variables');
        toggleSwitch.checked = false;

    }


}

setThemeFromLocalStorage();

toggleSwitch.addEventListener('change', () => {
    body.classList.toggle('dark-mode-variables');
    body.classList.toggle('light-mode-variables');


    const isDarkMode = body.classList.contains('dark-mode-variables');
    localStorage.setItem('theme', isDarkMode ? 'dark-mode-variables' : 'light-mode-variables');
    localStorage.setItem('isDarkMode', isDarkMode);

});
