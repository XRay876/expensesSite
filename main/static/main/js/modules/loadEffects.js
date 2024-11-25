const loadEffect = () => {
    var blocks = document.querySelectorAll('.money-block');
    blocks.forEach(function (block, index) {
        setTimeout(function () {
            block.classList.add('visible');
        }, index * 150);
    });
};

export default loadEffect;