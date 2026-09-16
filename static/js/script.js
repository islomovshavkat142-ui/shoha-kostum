// Инициализация Swiper
const swiper = new Swiper('.fabric-slider', {
    slidesPerView: 1,
    spaceBetween: 25,
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev'
    },
    breakpoints: {
        768: { slidesPerView: 2 },
        1200: { slidesPerView: 3 }
    }
});

// Твоя функция с эффектом прозрачности
function changeImg(id, src) {
    const mainImg = document.getElementById('main-img-' + id);
    if (mainImg) {
        mainImg.style.opacity = '0.4';
        setTimeout(() => {
            mainImg.src = src;
            mainImg.style.opacity = '1';
        }, 150);
    }
}

// Логика модального окна
const modal = document.getElementById("fabric-modal");

function openFabricModal(name, origin, price, text, comp, mainImg, extraImgs) {
    document.getElementById("modal-name").innerText = name;
    document.getElementById("modal-origin").innerText = origin;
    document.getElementById("modal-price").innerHTML = `Пошив: <span>${price}</span>`;
    document.getElementById("modal-text").innerText = text;
    document.getElementById("modal-comp").innerText = comp ? "Состав: " + comp : "";
    document.getElementById("modal-img").src = mainImg;

    const thumbs = document.getElementById("modal-thumbs");
    thumbs.innerHTML = '';

    const allPhotos = [mainImg, ...extraImgs.filter(i => i && i.trim() !== '')];

    if (allPhotos.length > 1) {
        allPhotos.forEach(src => {
            const img = document.createElement('img');
            img.src = src;
            img.className = 'modal-mini-thumb';
            img.onclick = () => {
                document.getElementById("modal-img").src = src;
            };
            thumbs.appendChild(img);
        });
    }

    modal.style.display = "flex";
    document.body.style.overflow = "hidden";
}

// Закрытие модалки
if (document.querySelector(".close-modal")) {
    document.querySelector(".close-modal").onclick = () => {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
    };
}

window.onclick = (e) => {
    if (e.target == modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
    }
};