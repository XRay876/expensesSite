import {hidePopup} from "./popup.js";
import {showNotification} from "./notifications.js";
import {createTransactionElement} from "./transactions.js";

const blockEvents = () => {
    const addTransactionBtn = document.getElementById('add-transaction-btn');
    const transactionFormContainer = document.getElementById('transaction-form-container');
    const transactionForm = document.getElementById('transaction-form');
    const transactionList = document.getElementById('transactions-list');
    const topUpForm = document.getElementById('top-up-form');


    if (addTransactionBtn) {
        addTransactionBtn.addEventListener('click', function () {
            if (transactionFormContainer.style.maxHeight === '0px' || transactionFormContainer.style.maxHeight === '') {
                transactionFormContainer.style.maxHeight = transactionFormContainer.scrollHeight + 'px';
            } else {
                transactionFormContainer.style.maxHeight = '0';
            }
        });
    }

    transactionForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(transactionForm);
        const blockId = document.getElementById('money_block_id').value;

        fetch('/add_transaction/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams(formData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    const noTransactionsElement = document.querySelector('.no-transactions');
                    if (noTransactionsElement) {
                        noTransactionsElement.remove();
                    }

                    let newLabel = document.querySelector('.new-label');
                    if (!newLabel) {
                        newLabel = document.createElement('li');
                        newLabel.className = 'new-label';

                        const newLabelSpan = document.createElement('span');
                        newLabelSpan.textContent = 'New';

                        newLabel.appendChild(newLabelSpan);

                        transactionList.insertBefore(newLabel, transactionList.firstChild);
                    }

                    const li = createTransactionElement(data.transaction, blockId);
                    transactionList.insertBefore(li, newLabel.nextSibling);

                    if (!blockTransactions[blockId]) {
                        blockTransactions[blockId] = [];
                    }

                    blockTransactions[blockId].unshift({
                        id: data.transaction.id,
                        date: data.transaction.date,
                        description: data.transaction.description,
                        amount: data.transaction.amount
                    });


                    const balanceElement = document.querySelector(`.balance[data-block-id="${blockId}"]`);
                    balanceElement.textContent = `${data.new_balance} ${data.currency}`;


                    transactionForm.reset();


                } else {

                    showNotification('Error creating a transaction', {isError: true});
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });

        transactionFormContainer.style.maxHeight = '0';
    });


    document.querySelectorAll('.delete-money-block').forEach((deleteBtn) => {
        deleteBtn.addEventListener('click', function (event) {
            event.stopPropagation();
            const blockElement = this.closest('.money-block');
            const blockId = blockElement.getAttribute('data-block-id');


            showNotification("Are you sure you want to delete this block?", {
                isConfirm: true,
                confirmCallback: function (confirmDelete) {
                    if (confirmDelete) {
                        fetch(`/delete_block/${blockId}/`, {
                            method: 'DELETE',
                            headers: {
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                            }
                        })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    blockElement.remove();
                                    showNotification("Block deleted successfully.");
                                } else {
                                    showNotification("Error deleting block.", {isError: true});
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                showNotification("Error deleting block.", {isError: true});
                            });
                    } else {

                    }
                }
            });
        });
    });

    document.getElementById('top-up-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        const blockId = document.getElementById('money_block_id_topup').value;


        const moneyBlockIdField = document.getElementById('money_block_id_topup');
        if (moneyBlockIdField) {
            moneyBlockIdField.value = blockId;

        } else {
            console.error('Error: Money block ID is missing.');
        }

        if (!blockId) {
            console.error("Error: Money block ID is missing.");
            return;
        }


        fetch('/top_up_balance/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams(formData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    const balanceElement = document.querySelector(`.balance[data-block-id="${blockId}"]`);
                    balanceElement.textContent = `${data.new_balance} ${data.currency}`;


                    const transactionList = document.getElementById('transactions-list');
                    const li = document.createElement('li');
                    li.textContent = `${data.transaction.date} - ${data.transaction.description}: ${data.transaction.amount}`;
                    transactionList.appendChild(li);

                    topUpForm.reset();

                    hidePopup('.popup-container-top-up', '.popup-content-top-up');
                    showNotification(data.message);
                } else {

                    showNotification(data.message, {isError: true});
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });

    });
};

export default blockEvents;