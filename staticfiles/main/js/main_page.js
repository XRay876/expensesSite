import { showPopup, hidePopup } from "./modules/popup.js";
import { showPopupGraphs, renderGraphs } from "./modules/graphs.js";
import { showNotification } from "./modules/notifications.js";
import { createTransactionElement, renderTransactions } from "./modules/transactions.js";

document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener('click', function (event) {
        const popupContainer = document.querySelector('.popup-container');
        const popupContent = document.querySelector('.popup-content');
        const popupContainerTransactions = document.querySelector('.popup-container-transactions');
        const popupContentTransactions = document.querySelector('.popup-content-transactions');
        const popupContainerTopUp = document.querySelector('.popup-container-top-up');
        const popupContentTopUp = document.querySelector('.popup-content-top-up');
        const popupContainerShare = document.querySelector('.share-popup-container');
        const popupContentShare = document.querySelector('.share-popup-content');
        const popupContainerGraphs = document.querySelector('.popup-container-graphs');
        const popupContentGraphs = document.querySelector('.popup-content-graphs');

        if (popupContainer && popupContainer.style.display === 'flex' && !popupContent.contains(event.target)) {
            hidePopup('.popup-container', '.popup-content');
        }

        if (popupContainerTransactions && popupContainerTransactions.style.display === 'flex' && !popupContentTransactions.contains(event.target)) {
            hidePopup('.popup-container-transactions', '.popup-content-transactions');
        }

        if (popupContainerTopUp && popupContainerTopUp.style.display === 'flex' && !popupContentTopUp.contains(event.target)) {
            hidePopup('.popup-container-top-up', '.popup-content-top-up');
        }

        if (popupContainerShare && popupContainerShare.style.display === 'flex' && !popupContentShare.contains(event.target)) {
            hidePopup('.share-popup-container', '.share-popup-content');
        }

        if (popupContainerGraphs && popupContainerGraphs.style.display === 'flex' && !popupContentGraphs.contains(event.target)) {
            hidePopup('.popup-container-graphs', '.popup-content-graphs');
        }

    });

    document.querySelectorAll('.add-block').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();
            showPopup('.popup-container', '.popup-content');
        });
    });


    const closeBtn = document.getElementById("add-close");
    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            hidePopup('.popup-container', '.popup-content');
        });
    }

    document.querySelectorAll('.top-up').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();

            const block = button.closest('.money-block');
            const blockId = block.getAttribute('data-block-id');


            const moneyBlockIdField = document.getElementById('money_block_id_topup');

            if (moneyBlockIdField) {
                moneyBlockIdField.value = blockId;

            } else {
                console.error('Error: Money block ID is missing.');
            }

            showPopup('.popup-container-top-up', '.popup-content-top-up');
        });
    });


    const closeBtnTopup = document.getElementById("add-close2");
    if (closeBtnTopup) {
        closeBtnTopup.addEventListener("click", function () {
            hidePopup('.popup-container-top-up', '.popup-content-top-up');
        });
    }

    document.getElementById('share-button').addEventListener('click', function () {

        const shareUrl = window.location.origin + '/user/' + uniqueLink + '/';

        document.getElementById('share-link').value = shareUrl;

    });
    document.querySelectorAll('.share-button').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();
            showPopup('.share-popup-container', '.share-popup-content');
        });
    });


    document.getElementById('copy-share-link').addEventListener('click', function () {
        const shareLinkInput = document.getElementById('share-link');
        shareLinkInput.select();
        shareLinkInput.setSelectionRange(0, 99999);

        navigator.clipboard.writeText(shareLinkInput.value).then(function () {
            showNotification('Link copied to clipboard!');
        }, function (err) {
            console.error('Could not copy text: ', err);
            showNotification('Could not copy the link, please copy it manually.', {isError : true});

        });
    });

    const closeBtnShare = document.getElementById("close-share-popup");
    if (closeBtnShare) {
        closeBtnShare.addEventListener("click", function () {
            hidePopup('.share-popup-container', '.share-popup-content');
        });
    }

    let currentBlockId = null;


    document.querySelectorAll('.graph-button').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();

            const block = button.closest('.money-block');
            const blockId = block.getAttribute('data-block-id');
            currentBlockId = blockId;

            showPopupGraphs(blockId);
        });
    });

    const graphsToggleOptions = document.querySelectorAll('.graphs-toggle-option');
    graphsToggleOptions.forEach(option => {
        option.addEventListener('click', function () {
            const graphType = this.getAttribute('data-graph-type');

            graphsToggleOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');

            renderGraphs(currentBlockId, graphType);
        });
    });

    const closeBtnGraph = document.getElementById("close-graphs");
    if (closeBtnGraph) {
        closeBtnGraph.addEventListener("click", function () {
            hidePopup('.popup-container-graphs', '.popup-content-graphs');
        });
    }



    document.querySelectorAll('.money-block').forEach((block, index) => {
        block.addEventListener('click', (event) => {
            event.stopPropagation();


            const blockId = block.getAttribute('data-block-id');
            document.getElementById('money_block_id').value = blockId;

            const transactions = blockTransactions[blockId];
            const transactionList = document.getElementById('transactions-list');
            transactionList.innerHTML = '';

            renderTransactions(blockId, transactions, transactionList);

            showPopup('.popup-container-transactions', '.popup-content-transactions');
        });
    });


    const closeBtnTransaction = document.getElementById("add-close1");
    if (closeBtnTransaction) {
        closeBtnTransaction.addEventListener("click", function () {
            hidePopup('.popup-container-transactions', '.popup-content-transactions');
        });
    }


    const addTransactionBtn = document.getElementById('add-transaction-btn');
    const transactionFormContainer = document.getElementById('transaction-form-container');
    if (addTransactionBtn) {
        addTransactionBtn.addEventListener('click', function () {
            // if (transactionFormContainer.style.display === 'none') {
            //     transactionFormContainer.style.display = 'block';
            // } else {
            //     transactionFormContainer.style.display = 'none';
            // }
            if (transactionFormContainer.style.maxHeight === '0px' || transactionFormContainer.style.maxHeight === '') {
                transactionFormContainer.style.maxHeight = transactionFormContainer.scrollHeight + 'px';
            } else {
                transactionFormContainer.style.maxHeight = '0';
            }
        });
    }


    const transactionForm = document.getElementById('transaction-form');
    const transactionList = document.getElementById('transactions-list');

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

                    showNotification('Error creating a transaction', {isError : true});
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


    const top_up_form = document.getElementById('top-up-form');

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

                    top_up_form.reset();

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


});
