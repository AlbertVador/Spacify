const itemIds = document.getElementById("varItemIds").innerHTML.split(',');
var currentItemIndex = 0

function formatSource(itemId) {
    return ["/image/",itemId].join("")
}

function setImageSource(itemIndex) {
    document.getElementById("itemImage").src=formatSource(itemIds[itemIndex])
}

function setItem(itemIndex) {
    setImageSource(itemIndex)
}

function nextItem() {
    setItem(++currentItemIndex)
}

setItem(currentItemIndex)