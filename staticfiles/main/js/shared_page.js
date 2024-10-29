import { showPopup, hidePopup } from "./modules/popup.js";
import { showPopupGraphs, renderGraphs } from "./modules/graphs-shared.js";
import { renderTransactions } from "./modules/transactions-shared.js";


document.addEventListener("DOMContentLoaded", function () {

    let currentBlockId = null;

    document.querySelectorAll('.money-block-shared').forEach((block) => {
        block.addEventListener('click', (event) => {
            event.stopPropagation();

            const blockId = block.getAttribute('data-block-id');
            const transactions = blockTransactions[blockId];

            renderTransactions(transactions);

            showPopup('.popup-container-transactions-shared', '.popup-content-transactions-shared');
        });
    });

    const closeBtn = document.getElementById("add-close4");
    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            hidePopup('.popup-container-transactions-shared', '.popup-content-transactions-shared');
        });
    }

    document.addEventListener('click', function (event) {
        const popupContainerShared = document.querySelector('.popup-container-transactions-shared');
        const popupContentShared = document.querySelector('.popup-content-transactions-shared');
        const popupContainerGraphs = document.querySelector('.popup-container-graphs');
        const popupContentGraphs = document.querySelector('.popup-content-graphs');


        if (popupContainerShared && popupContainerShared.style.display === 'flex' && !popupContentShared.contains(event.target)) {
            hidePopup('.popup-container-transactions-shared', '.popup-content-transactions-shared');
        }

        if (popupContainerGraphs && popupContainerGraphs.style.display === 'flex' && !popupContentGraphs.contains(event.target)) {
            hidePopup('.popup-container-graphs', '.popup-content-graphs');
        }
    });


    document.querySelectorAll('.graph-button').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();

            const block = button.closest('.money-block-shared');
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

});


