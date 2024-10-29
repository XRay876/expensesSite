import {showNotification} from "./notifications.js";
import {renderMonthlyExpensesChart, renderDailyTopupsChart, renderMonthlyTopupsChart, renderDailyExpensesChart} from "./graphs.js";

export function showPopupGraphs(blockId) {
    const popupContainer = document.querySelector('.popup-container-graphs');
    const popupContent = document.querySelector('.popup-content-graphs');
    popupContainer.style.display = 'flex';

    requestAnimationFrame(() => {
        popupContainer.classList.add('active');
        popupContent.style.opacity = 1;
        popupContent.style.transform = 'scale(1)';
    });


    const graphsToggleOptions = document.querySelectorAll('.graphs-toggle-option');
    graphsToggleOptions.forEach(option => {
        if (option.getAttribute('data-graph-type') === 'expenses') {
            option.classList.add('active');
        } else {
            option.classList.remove('active');
        }
    });

    renderGraphs(blockId, 'expenses');
}


export function renderGraphs(blockId, graphType) {

    let fetchUrl = `/user/${uniqueLink}/get_graph_data/${blockId}/`;
    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            if (graphType === 'expenses') {
                const dailyExpensesData = data.daily_expenses;
                const monthlyExpensesData = data.monthly_expenses;

                renderDailyExpensesChart(dailyExpensesData);
                renderMonthlyExpensesChart(monthlyExpensesData);
            } else if (graphType === 'topups') {
                const dailyTopupsData = data.daily_topups;
                const monthlyTopupsData = data.monthly_topups;

                renderDailyTopupsChart(dailyTopupsData);
                renderMonthlyTopupsChart(monthlyTopupsData);
            }
        })
        .catch(error => {
            console.error('Error fetching graph data:', error);
            showNotification('Error fetching graph data', {isError : true});
        });
}