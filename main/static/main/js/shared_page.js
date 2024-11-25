import loadEffect from "./modules/loadEffects.js";
import displaySharedPopup from "./modules/popupSharedDisplay.js";
import theme from "./modules/theme.js";
import currency from "./modules/currency.js";

async function safeExecute(func) {
    try {
        await func();
    } catch (error) {
        console.error(`Error in ${func.name}:`, error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    safeExecute(theme);
    safeExecute(currency);
    safeExecute(loadEffect);
    safeExecute(displaySharedPopup);
});


