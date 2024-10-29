import { showNotification } from "./notifications.js";

export function createTransactionElement(transaction, blockId, includeDate = true) {
    const li = document.createElement('li');
    li.classList.add('transaction-item')

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

    const deleteIcon = document.createElement('i');

    deleteIcon.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" class="transaction-delete-icon" viewBox="0 0 24 24" width="16" height="16">
        <path fill="currentColor" d="M3 6h18v2H3V6zm2 3h14l-1 13H6L5 9zm5-5h4v2h-4V4z"/>
    </svg>
`;
    deleteIcon.addEventListener('click', function (event) {
        event.stopPropagation();
        deleteTransaction(transaction.id, blockId, li);
    });

    const amountAndDeleteContainer = document.createElement('div');
    amountAndDeleteContainer.classList.add('amount-delete-container');
    amountAndDeleteContainer.appendChild(amountElement);
    amountAndDeleteContainer.appendChild(deleteIcon);


    const mainContent = document.createElement('div');
    mainContent.classList.add('transaction-main-content');

    mainContent.appendChild(descriptionElement);
    mainContent.appendChild(amountAndDeleteContainer);


    li.appendChild(timeElement);
    li.appendChild(mainContent);

    return li;
}

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

export function renderTransactions(blockId, transactions, transactionList) {
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
                const li = createTransactionElement(transaction, blockId, false);
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

function deleteTransaction(transactionId, blockId, transactionElement) {

    const transactionList = document.getElementById('transactions-list');

    fetch(`/delete_transaction/${transactionId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })

        .then(response => response.json())
        .then(data => {
            if (data.success) {

                showNotification('Transaction deleted');
                transactionElement.remove();

                const moneyBlock = document.querySelector(`.money-block[data-block-id="${blockId}"]`);
                const balanceElement = document.querySelector(`.balance[data-block-id="${blockId}"]`);
                balanceElement.textContent = `${data.new_balance} ${data.currency}`;


                blockTransactions[blockId] = blockTransactions[blockId].filter(t => t.id !== transactionId);

                transactionList.innerHTML = '';
                renderTransactions(blockId, blockTransactions[blockId], transactionList);


            } else {
                showNotification('Error deleting the transaction', {isError: true});
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}