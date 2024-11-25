const exportExcel = () => {
    document.getElementById('export-button').addEventListener('click', function () {
        var table = document.getElementById('planning-table');
        var wb = XLSX.utils.table_to_book(table, {sheet: "Planning Data"});
        XLSX.writeFile(wb, 'PlanningData' + '.xlsx');
    });
};

export default exportExcel;