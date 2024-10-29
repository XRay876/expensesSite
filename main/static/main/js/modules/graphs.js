import { showNotification } from "./notifications.js";

export {renderDailyExpensesChart, renderMonthlyExpensesChart, renderMonthlyTopupsChart, renderDailyTopupsChart};

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
    let fetchUrl = `/get_graph_data/${blockId}/`;
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

function renderDailyExpensesChart(dailyExpensesData) {

    const labels = dailyExpensesData.map(item => {
        const [year, month, day] = item.day.split('-');
        const date = new Date(year, month - 1, day);
        return date.toLocaleDateString(undefined, {day: 'numeric', month: 'short'});
    });
    const dataPoints = dailyExpensesData.map(item => item.total);

    if (window.dailyChart) {
        window.dailyChart.destroy();
    }
    const ctx = document.getElementById('daily-chart').getContext('2d');
    window.dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily expences',
                data: dataPoints,
                fill: false,
                borderColor: 'rgba(75,192,192,0.45)',
                backgroundColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            plugins: {

                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (context) {
                            return `Amount: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(200, 200, 200, 0.2)'
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }

        }
    });

}

function renderMonthlyExpensesChart(monthlyExpensesData) {
    const labels = monthlyExpensesData.map(item => {
        const date = new Date(item.month + '-02');
        return date.toLocaleDateString(undefined, {month: 'long'});
    });
    const dataPoints = monthlyExpensesData.map(item => item.total);

    if (window.monthlyChart) {
        window.monthlyChart.destroy();
    }

    const ctx = document.getElementById('monthly-chart').getContext('2d');
    window.monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly expences',
                data: dataPoints,
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgb(255, 99, 132)',
                borderWidth: 1
            }]
        },
        options: {
            plugins: {

                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (context) {
                            return `Amount: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {

                    grid: {
                        display: false
                    }
                },
                y: {

                    grid: {
                        color: 'rgba(200, 200, 200, 0.2)'
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

function renderDailyTopupsChart(dailyTopupsData) {
    const labels = dailyTopupsData.map(item => {
        const [year, month, day] = item.day.split('-');
        const date = new Date(year, month - 1, day);
        return date.toLocaleDateString(undefined, {day: 'numeric', month: 'short'});
    });
    const dataPoints = dailyTopupsData.map(item => item.total);

    if (window.dailyChart) {
        window.dailyChart.destroy();
    }

    const ctx = document.getElementById('daily-chart').getContext('2d');
    window.dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Topups',
                data: dataPoints,
                fill: false,
                borderColor: 'rgba(153, 102, 255, 0.4)',
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                tension: 0.1,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            plugins: {

                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (context) {
                            return `Amount: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(200, 200, 200, 0.2)'
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }

        }
    });

}

function renderMonthlyTopupsChart(monthlyTopupsData) {
    const labels = monthlyTopupsData.map(item => {
        const date = new Date(item.month + '-02');
        return date.toLocaleDateString(undefined, {month: 'long'});
    });
    const dataPoints = monthlyTopupsData.map(item => item.total);

    if (window.monthlyChart) {
        window.monthlyChart.destroy();
    }

    const ctx = document.getElementById('monthly-chart').getContext('2d');
    window.monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily Topups',
                data: dataPoints,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                minBarLength: 5,
            }]
        },
        options: {
            plugins: {

                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (context) {
                            return `Amount: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {

                    grid: {
                        display: false
                    }
                },
                y: {

                    grid: {
                        color: 'rgba(200, 200, 200, 0.2)'
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }
            },

            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });

}