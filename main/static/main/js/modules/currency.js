const currency = () => {
    const toggleButton = document.getElementById('toggle-currency-block');
    const exchangeRatesWrapper = document.querySelector('.exchange-rates-wrapper');
    const toggleArrow = document.getElementById('toggle-arrow');
    let isRatesVisible = false;

    exchangeRatesWrapper.style.maxHeight = '0';

    function setMaxHeight() {
        exchangeRatesWrapper.style.maxHeight = exchangeRatesWrapper.scrollHeight + 'px';
    }

    toggleButton.addEventListener('click', function () {
        if (isRatesVisible) {
            exchangeRatesWrapper.style.maxHeight = '0';
            toggleArrow.style.transform = 'rotate(0deg)';

        } else {
            setMaxHeight();

            toggleArrow.style.transform = 'rotate(180deg)';
        }
        isRatesVisible = !isRatesVisible;
    });


    window.addEventListener('resize', function () {
        if (isRatesVisible) {
            setMaxHeight();
        }
    });

    const baseCurrency = 'USD';
    const currencies = ['CAD', 'EUR', 'KZT', 'RUB'];
    const apiUrl = `https://api.exchangerate-api.com/v4/latest/${baseCurrency}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const rates = data.rates;
            const exchangeRatesDiv = document.getElementById('exchange-rates');
            currencies.forEach(currency => {
                const rate = rates[currency];
                if (rate) {
                    const rateDiv = document.createElement('div');
                    rateDiv.classList.add('exchange-rate');
                    rateDiv.innerHTML = `
                        <strong>${currency}</strong>
                        <span>1 ${baseCurrency} = ${rate.toFixed(2)} ${currency}</span>
                    `;
                    exchangeRatesDiv.appendChild(rateDiv);
                }
            });
        })
        .catch(error => {
            console.error('Error with parsing currency:', error);
            const exchangeRatesDiv = document.getElementById('exchange-rates');
            exchangeRatesDiv.innerHTML = '<p>Error with parsing currency</p>';
        });
};

export default currency;
