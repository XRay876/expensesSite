const aiTable = document.getElementById('ai-table');
const errorList = document.getElementById('error-ai-list');
const table = document.getElementById('planning-table');

const aiResponse = () => {
    document.getElementById('ai-button').addEventListener('click', function () {
        addLoading();

        let headers = [];
        let headerCells = table.rows[0].cells;
        for (let i = 0; i < headerCells.length; i++) {
            headers.push(headerCells[i].innerText.trim());
        }
        let data = [];

        for (let col = 0; col < headers.length; col++) {
            let columnData = {
                "Name": headers[col],
                "Balance": "",
                "Transactions": [],
                "Top up": [],
                "Additional info": []
            };

            for (let row = 1; row < table.rows.length; row++) {
                let cell = table.rows[row].cells[col];

                if (cell) {
                    let cellText = cell.innerText.trim().replace(/\n/g, ' ');
                    if (cellText) {
                        if (row === 1) {
                            columnData["Balance"] = cellText;
                        } else if (cellText.toLowerCase().includes("top up")) {
                            columnData["Top up"].push(cellText);
                        } else if (!cellText.toLowerCase().includes("transaction")) {
                            columnData["Additional info"].push(cellText);
                        } else {
                            columnData["Transactions"].push(cellText);
                        }
                    }
                }
            }

            data.push(columnData);
        }



        fetch('/planning/process_ai_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({'data': JSON.stringify(data)}),
        })
            .then(response => {

                return response.json();
            })
            .then(data => {

                if (data.processed_data) {
                    updateTable(data.processed_data);
                    cleanList(errorList);
                    aiTable.classList.add('shown');
                } else if (data.error) {
                    addError();
                } else {
                    addError();
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                addError();
            });
    });
};

function updateTable(processedData) {
    const table = document.getElementById('table-ai');
    const tbody = table.getElementsByTagName('tbody')[0];

    tbody.innerHTML = '';

    for (const [sectionName, sectionData] of Object.entries(processedData)) {
        const headerRow = document.createElement('tr');
        const headerCell = document.createElement('th');
        headerCell.colSpan = 2;
        headerCell.textContent = sectionName;
        headerRow.appendChild(headerCell);
        tbody.appendChild(headerRow);

        if (Array.isArray(sectionData)) {

            sectionData.forEach(item => {

                for (const [key, value] of Object.entries(item)) {
                    const row = document.createElement('tr');

                    const keyCell = document.createElement('td');
                    keyCell.textContent = key;
                    row.appendChild(keyCell);

                    const valueCell = document.createElement('td');
                    valueCell.textContent = value;
                    row.appendChild(valueCell);

                    tbody.appendChild(row);
                }

                const emptyRow = document.createElement('tr');
                const emptyCell = document.createElement('td');
                emptyCell.colSpan = 2;
                emptyCell.innerHTML = '<hr>';
                emptyRow.appendChild(emptyCell);
                tbody.appendChild(emptyRow);
            });
        } else if (typeof sectionData === 'object') {

            for (const [key, value] of Object.entries(sectionData)) {
                const row = document.createElement('tr');

                const keyCell = document.createElement('td');
                keyCell.textContent = key;
                row.appendChild(keyCell);

                const valueCell = document.createElement('td');
                valueCell.textContent = value;
                row.appendChild(valueCell);

                tbody.appendChild(row);
            }
        } else {
            const row = document.createElement('tr');

            const keyCell = document.createElement('td');
            keyCell.textContent = sectionName;
            row.appendChild(keyCell);

            const valueCell = document.createElement('td');
            valueCell.textContent = sectionData;
            row.appendChild(valueCell);

            tbody.appendChild(row);
        }
    }
}

function cleanList(list) {
    while (list.firstChild) {
        list.removeChild(list.firstChild);
    }
}

function addError() {
    cleanList(errorList);
    const pElement = document.createElement('p');
    pElement.textContent = 'Please try again';
    pElement.classList.add('errorMessageText');
    errorList.appendChild(pElement);
    setTimeout(() => {
        errorList.removeChild(pElement)
    }, 2000);
}

function addLoading() {
    cleanList(errorList);
    const pElement = document.createElement('p');
    pElement.textContent = 'Thinking...';
    pElement.classList.add('loadingMessageText');
    errorList.appendChild(pElement);
}

export default aiResponse;