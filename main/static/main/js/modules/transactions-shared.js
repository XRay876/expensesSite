function groupTransactionsByDate(transactions) {
    const groupedTransactions = [];
    let lastDate = null;

    transactions.forEach(function (transaction) {
        const dateObj = new Date(transaction.date);
        const dateKey = dateObj.toLocaleDateString(undefined, {day: 'numeric', month: 'long'});
        if (lastDate !== dateKey) {
            groupedTransactions.push({
                date: dateKey,
                transactions: [transaction]
            });
            lastDate = dateKey;
        } else {
            groupedTransactions[groupedTransactions.length - 1].transactions.push(transaction);
        }
    });

    return groupedTransactions;
}
function createTransactionElement(transaction) {
    const li = document.createElement('li');
    li.classList.add('transaction-item');

    const amount = transaction.amount;
    let amountText = '';
    let amountClass = '';
    let arrow = '';

    if (amount > 0) {
        amountText = `+${amount}`;
        amountClass = 'transaction-topup';
        arrow = '↑';
    } else if (amount < 0) {
        amountText = `${amount}`;
        amountClass = 'transaction-expense';
        arrow = '↓';
    } else {
        amountText = `${amount}`;
    }

    const dateObj = new Date(transaction.date);
    const formattedTime = dateObj.toLocaleTimeString(undefined, {hour: '2-digit', minute: '2-digit'});

    const timeElement = document.createElement('span');
    timeElement.textContent = formattedTime;
    timeElement.classList.add('transaction-time');

    const descriptionElement = document.createElement('div');
    descriptionElement.textContent = transaction.description;
    descriptionElement.classList.add('transaction-description');

    const amountElement = document.createElement('div');
    amountElement.innerHTML = `${amountText} ${arrow}`;
    amountElement.classList.add('transaction-amount', amountClass);

    const mainContent = document.createElement('div');
    mainContent.classList.add('transaction-main-content');

    mainContent.appendChild(descriptionElement);
    mainContent.appendChild(amountElement);

    li.appendChild(timeElement);
    li.appendChild(mainContent);

    return li;
}
export function renderTransactions(transactions) {
        const transactionList = document.getElementById('transactions-list');
        transactionList.innerHTML = '';

        if (transactions && transactions.length > 0) {
            const groupedTransactions = groupTransactionsByDate(transactions);

            groupedTransactions.forEach(function (group) {

                const dateLi = document.createElement('li');
                dateLi.classList.add('date-heading');

                const dateSpan = document.createElement('span');
                dateSpan.textContent = group.date;
                dateLi.appendChild(dateSpan);
                transactionList.appendChild(dateLi);

                group.transactions.forEach(function (transaction) {
                    const li = createTransactionElement(transaction);
                    transactionList.appendChild(li);
                });
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No transactions';
            li.classList.add('no-transactions');
            transactionList.appendChild(li);
        }
    }