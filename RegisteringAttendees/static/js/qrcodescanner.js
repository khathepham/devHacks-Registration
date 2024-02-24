// import {Html5QrcodeScanner} from "html5-qrcode"
// Html5QrcodeScanner = require("html5-qrcode")
// const {XMLHttpRequest} = require("xmlhttprequest");
// const {Html5QrcodeScanner} = require("html5-qrcode");
let takingABreak = false;
const BreakTime = 2; //seconds
let day = "Saturday"
let mode = "Standard"

function onScanSuccess(decodedText, decodedResult) {
    // handle the scanned code as you like, for example:
    html5QrcodeScanner.pause();
    decodedText = decodedText.replace(".png", "")

    if(decodedText.length === 6){
        checkinTicket(decodedText)
    }

    else{
        createFailureToast(`${decodedText} is an invalid ticket code.`)
    }

    console.log(`Code matched = ${decodedText}`, decodedResult);
    setTimeout(endBreak, BreakTime*1000)
}

function startBreak(){
    takingABreak = true;
}

function endBreak(){
    takingABreak = false;
    html5QrcodeScanner.resume();
}

function onScanFailure(error) {
    // handle scan failure, usually better to ignore and keep scanning.
    // for example:
    // console.warn(`Code scan error = ${error}`);
}

let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader",
    { fps: 10, qrbox: {width: 250, height: 250} },
    /* verbose= */ false);
html5QrcodeScanner.render(onScanSuccess, onScanFailure);



//Testing Button
const toastTrigger = document.getElementById('liveToastBtn')

if (toastTrigger) {
    toastTrigger.addEventListener('click', () => {

        checkinTicket("AABBCC")
    })
}

function createSuccessToast(message){
    if ("content" in document.createElement("template")) {
        const toastContainer = document.getElementById("toastContainer");
        const template = document.querySelector("#toastTemplate")

        const clone = template.content.cloneNode(true);
        let toastBody = clone.querySelector(".toast-body");
        toastBody.textContent = message;
        let toast = clone.querySelector(".toast");
        toast.classList.add("text-bg-success");

        toastContainer.appendChild(clone)
        const allToasts = toastContainer.querySelectorAll(".toast")
        const newToast = allToasts[allToasts.length - 1]
        let bsToast = bootstrap.Toast.getOrCreateInstance(newToast)
        bsToast.show()
        setTimeout(deleteSelf, 5000, newToast)
    }
}

function createFailureToast(message){
    if ("content" in document.createElement("template")) {
        const toastContainer = document.getElementById("toastContainer");
        const template = document.querySelector("#toastTemplate")

        const clone = template.content.cloneNode(true);
        let toastBody = clone.querySelector(".toast-body");
        toastBody.textContent = message;
        let toast = clone.querySelector(".toast");
        toast.classList.add("text-bg-danger");

        toastContainer.appendChild(clone)
        const allToasts = toastContainer.querySelectorAll(".toast")
        const newToast = allToasts[allToasts.length - 1]
        let bsToast = bootstrap.Toast.getOrCreateInstance(newToast)
        bsToast.show()
        setTimeout(deleteSelf, 5000, newToast)
    }
}

function createWarningToast(message){
    if ("content" in document.createElement("template")) {
        const toastContainer = document.getElementById("toastContainer");
        const template = document.querySelector("#toastTemplate")

        const clone = template.content.cloneNode(true);
        let toastBody = clone.querySelector(".toast-body");
        toastBody.textContent = message;
        let toast = clone.querySelector(".toast");
        toast.classList.add("text-bg-warning");

        toastContainer.appendChild(clone)
        const allToasts = toastContainer.querySelectorAll(".toast")
        const newToast = allToasts[allToasts.length - 1]
        let bsToast = bootstrap.Toast.getOrCreateInstance(newToast)
        bsToast.show()
        setTimeout(deleteSelf, 5000, newToast)
    }
}

function deleteSelf(element){
    element.remove()
}

function checkinTicket(ticketCode){
    const url = "https://devhacks2024.khathepham.com/register-devhacks-2024/checkin"
    const request = new XMLHttpRequest()
    const body = {ticketCode: ticketCode, day: day}

    if (mode !== "Standard") {
        body["meal"] = mode;
        body["mealGroups"] = ["DR"]
        if(AButton.checked){
            body.mealGroups.push("A")
        }
        if(BButton.checked){
            body.mealGroups.push("B")
        }
        if(CButton.checked){
            body.mealGroups.push("C")
        }
    }

    request.open("POST", url, false);
    request.setRequestHeader("Content-Type", "application/json")
    request.onload = (e) => {
        if (request.status >= 200 && request.status <= 249){
            createSuccessToast(request.responseText)
        }
        else if (request.status >= 250 && request.status <= 299){
            createWarningToast(request.responseText)
        }
        else {
            createFailureToast(request.responseText)
        }
        console.log(request.responseText)
    }
    request.onerror = (e) => {
        createFailureToast(request.statusText)
    }

    request.send(JSON.stringify(body))
}

let fridayButton = document.getElementById("FridayCheckin")
let saturdayButton = document.getElementById("SaturdayCheckin")

if(fridayButton){
    fridayButton.addEventListener('click', () => {
        day = "Friday"
    })
}

if(saturdayButton){
    saturdayButton.addEventListener('click', () => {
        day = "Saturday"
    })
}

let standardButton = document.getElementById("Standard")
let mealGroupsDiv = document.getElementById("mealGroups")
if(standardButton){
    standardButton.addEventListener('click', () => {
        mealGroupsDiv.hidden = true;
        mode = "Standard"
    })
}

let lunchButton = document.getElementById("Lunch")
let dinnerButton = document.getElementById("Dinner")

if (lunchButton) {
    lunchButton.addEventListener('click', () => {
        mealGroupsDiv.hidden = false;
        mode = "Lunch"
    })
}

if (dinnerButton) {
    dinnerButton.addEventListener('click', () => {
        mealGroupsDiv.hidden = false;
        mode = "Dinner"
    })
}

let DRButton = document.getElementById("DietaryRestrictions")
let AButton = document.getElementById("A")
let BButton = document.getElementById("B")
let CButton = document.getElementById("C")
let mealGroupButtons = [DRButton, AButton, BButton, CButton]