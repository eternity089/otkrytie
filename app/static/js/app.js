
const items = document.querySelectorAll("#city .dropdown-item");
const button = document.querySelector(".dropdown-toggle");
const input = document.getElementById("city-input");

//управление выбором города и подставка адресов под соответствующий город
items.forEach(item => {
    item.addEventListener("click", function (e) {
        e.preventDefault();
        const cityName = this.textContent;
        const cityId = this.dataset.id;
        if (button) button.textContent = cityName;
        if (input) input.value = cityId;
        items.forEach(i => i.classList.remove("active"));
        this.classList.add("active");
        fetch(`/set-city/?city_id=${cityId}`, {
            method: "GET",
            credentials: "same-origin"
        })
        .then(res => res.json())
        .then(data => {
            const citySpan = document.getElementById("current-city-name");
            if (citySpan && data.city_name) {
                citySpan.textContent = data.city_name;
            }
            const input = document.getElementById("city-input");
            if (input) input.value = cityId;
            const addressButton = document.getElementById("addressDropdown");
            const addressInput = document.getElementById("addressInput");
            if (addressButton) addressButton.textContent = "Выберите адрес";
            if (addressInput) addressInput.value = "";
            return fetch(`/get-addresses/?city_id=${cityId}`);
        })
        .then(res => res.json())
        .then(data => {
            const addressList = document.getElementById("address-list");
            const addressButton = document.getElementById("addressDropdown");
            const addressInput = document.getElementById("addressInput");
            if (!addressList) return;
            addressList.innerHTML = '';
            if (!data.data.length) {
                addressList.innerHTML = '<li><span class="dropdown-item-text">Нет адресов</span></li>';
                return;
            }
            data.data.forEach((address, index) => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <a href="#" class="dropdown-item address-item" data-id="${address.id}">
                        ${address.name}
                    </a>
                `;
                addressList.appendChild(li);
            });
            document.querySelectorAll(".address-item").forEach(addr => {
                addr.addEventListener("click", function(e) {
                    e.preventDefault();
                    const addressName = this.textContent;
                    const addressId = this.dataset.id;
                    if (addressButton) addressButton.textContent = addressName;
                    if (addressInput) addressInput.value = addressId;
                    document.querySelectorAll(".address-item").forEach(i => i.classList.remove("active"));
                    this.classList.add("active");
                    fetch(`/set-address/?address_id=${addressId}`, {
                        method: "GET",
                        credentials: "same-origin"
                    });
                });
            });
            const firstAddress = document.querySelector(".address-item");
            if (firstAddress) {
                firstAddress.click();
            }
        });
    });
});

//добавление товара в корзину через кнопку
toCart = async(target,pk) => {
    const res = await fetch(`/to_cart/${pk}`).then(res => res.json())
    if(res.count){
        target.classList.remove('btn-outline-danger')
        target.classList.add('btn-outline-success')
        target.textContent = 'Товар в корзине'
    } else{
        target.classList.remove('btn-outline-danger')
        target.classList.add('btn-outline-disabled')
        target.textContent = 'больше добавить нельзя'
    }
    setTimeout(() => {
        target.textContent = 'В корзину'
        target.classList.remove('btn-outline-success')
        target.classList.add('btn-outline-danger')
    }, 1000)

    await updateCartUI()
}

//обновление общего количества и стоимости товаров в корзимне
window.updateCartUI = async function() {
    const res = await fetch('/get-cart-total/');
    const data = await res.json();

    const { total_count, total_price } = data;

    document.querySelectorAll('.cart-count').forEach(el => {
        el.textContent = total_count;
    });

    const totalEl = document.getElementById('cart-total');
    if (totalEl) {
        totalEl.textContent = total_price;
    }
}