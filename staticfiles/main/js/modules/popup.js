export function showPopup(popupContainerSelector, popupContentSelector) {
    const popupContainer = document.querySelector(popupContainerSelector);
    const popupContent = document.querySelector(popupContentSelector);
    popupContainer.style.display = 'flex';

    requestAnimationFrame(() => {
        popupContainer.classList.add('active');
        popupContent.style.opacity = 1;
        popupContent.style.transform = 'scale(1)';
    });
}

export function hidePopup(popupContainerSelector, popupContentSelector) {
    const popupContainer = document.querySelector(popupContainerSelector);
    const popupContent = document.querySelector(popupContentSelector);
    popupContainer.classList.remove('active');
    popupContent.style.opacity = 0;
    popupContent.style.transform = 'scale(0.8)';

    setTimeout(() => {
        popupContainer.style.display = 'none';
    }, 300);
}


