import exportExcel from "./modules/exportExcel.js";
import aiResponse from "./modules/aiResponseTable.js";
import theme from "./modules/theme.js";
import currency from "./modules/currency.js";

async function safeExecute(func) {
    try {
        await func();
    } catch (error) {
        console.error(`Error in ${func.name}:`, error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    safeExecute(exportExcel);
    safeExecute(aiResponse);
    safeExecute(theme);
    safeExecute(currency);
});