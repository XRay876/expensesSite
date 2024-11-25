import {showPopup, hidePopup} from "./popup.js";
import {showNotification} from "./notifications.js";
import {renderTransactions} from "./transactions.js";
import { showPopupGraphs, renderGraphs } from "./graphs.js";

const displayPopup = () => {

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


    document.addEventListener('click', function (event) {
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

    document.getElementById('add-block-id').addEventListener('click', (event) => {
        event.stopPropagation();
        showPopup('.popup-container', '.popup-content');
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
    document.getElementById('share-button').addEventListener('click', (event) => {
            event.stopPropagation();
            showPopup('.share-popup-container', '.share-popup-content');

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
}


export default displayPopup;