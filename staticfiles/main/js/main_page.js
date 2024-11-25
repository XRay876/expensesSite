
import displayPopup from "./modules/popupDisplay.js";
import theme from "./modules/theme.js";
import currency from "./modules/currency.js";
import blockEvents from "./modules/blockEvents.js";
import loadEffect from "./modules/loadEffects.js";

async function safeExecute(func) {
    try {
        await func();
    } catch (error) {
        console.error(`Error in ${func.name}:`, error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    safeExecute(loadEffect);
    safeExecute(theme);
    safeExecute(currency);
    safeExecute(displayPopup);
    safeExecute(blockEvents);
});
