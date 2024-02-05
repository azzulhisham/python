// const chart = document.querySelector("#map");

// new Chart(chart, {
//     type: 'line',
//     data: {
//         labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'],
//         datasets: [
//             {
//                 label: 'TSS Northbound',
//                 data: [1011, 1000, 1023, 1080, 1091, 1100, 1201, 1210, 1220, 1290, 1300, 1333],
//                 borderColor: 'red',
//                 borderWidth: 2
//             }
//         ]
//     },
//     options: {
//         responsive: true
//     }
// })


// constant
const cnt_in_TSS_N = document.getElementById("cnt_in_TSS_N")
const cnt_in_TSS_S = document.getElementById("cnt_in_TSS_S")
const cnt_left_TSS_N = document.getElementById("cnt_left_TSS_N")
const cnt_left_TSS_S = document.getElementById("cnt_left_TSS_S")


///////////////////
//     mapbox
///////////////////
// Create a popup, but don't add it to the map yet.
const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
});

mapboxgl.accessToken = 'pk.eyJ1IjoiYXp6dWxoaXNoYW0iLCJhIjoiY2s5bjR1NDBqMDJqNDNubjdveXdiOGswYyJ9.SYlfXRzRtpbFoM2PHskvBg';
const map = new mapboxgl.Map({
    container: 'map', // container ID
    // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
    style: 'mapbox://styles/mapbox/satellite-streets-v12', // style URL
    center: [100.441885, 3.869975], // starting position [lng, lat]  
    zoom: 5, // starting zoom
    pitch: 30
});

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());

map.on('load', ()=> {
    map.setFog();
});

/////////////////////////////////////////////////////////
// JavaScript example using WebSocket object
// Create a WebSocket object with the URL of the server
/////////////////////////////////////////////////////////
const ws_URL = "ws://MYKUL-MBP-02.local:28383";
let ws = new WebSocket(ws_URL);

// Define a heartbeat interval in milliseconds
const HEARTBEAT_INTERVAL = 30000;

// Define a variable to store the heartbeat timeout ID
let heartbeatTimeout;
lst_vessel = {};
init_WebSocket();

function init_WebSocket(){
    // Add an event listener for when the connection is opened
    ws.addEventListener("open", function(event) {
        // Send a message to the server
        // ws.send("Hello Server!");
        // Start the heartbeat timeout

        startHeartbeat();
        ws.send('-')
        // var interval = setInterval(getData, 10);
    });

    // Add an event listener for when a message is received from the server
    ws.addEventListener("message", function(event) {
        // Log the message from the server
        console.log("Message from server: " + event.data);
        data = JSON.parse(event.data)
        cnt_in_TSS_N.innerText = data['cnt_in_TSS_N']
        cnt_in_TSS_S.innerText = data['cnt_in_TSS_S']
        cnt_left_TSS_N.innerText = data['cnt_left_TSS_N']
        cnt_left_TSS_S.innerText = data['cnt_left_TSS_S']


        // Reset the heartbeat timeout
        resetHeartbeat();
    });

    // Add an event listener for when an error occurs
    ws.addEventListener("error", function(event) {
        // Log the error
        console.log("Error: " + event.message);
    });

    // Add an event listener for when the connection is closed
    ws.addEventListener("close", function(event) {
        // Log the close code and reason
        console.log("Connection closed: " + event.code + " " + event.reason);
        // Clear the heartbeat timeout
        clearHeartbeat();

        alert("Connection closed: " + event.code + " " + event.reason)
        //setTimeout(reconnect_ws, 5000);
        location.reload();
    });
}


function reconnect_ws(){
    remove_WebSocket
    ws = new WebSocket(ws_URL);
    init_WebSocket
}

function startHeartbeat() {
    // Set a timeout to send a ping message after the heartbeat interval
    heartbeatTimeout = setTimeout(function() {
        // Send a ping message and log it
        ws.send("ping");
        console.log("Send a ping message!");
        // Start the heartbeat timeout again
        startHeartbeat();
    }, HEARTBEAT_INTERVAL);
}

// Define a function to reset the heartbeat timeout
function resetHeartbeat() {
    // Clear the existing heartbeat timeout
    clearHeartbeat();
    // Start the heartbeat timeout again
    startHeartbeat();
}

// Define a function to clear the heartbeat timeout
function clearHeartbeat() {
    // Clear the existing heartbeat timeout if any
    if (heartbeatTimeout) {
        clearTimeout(heartbeatTimeout);
        heartbeatTimeout = null;
    }
}





const menuBtn = document.querySelector('#menu-btn')
const closeBtn = document.querySelector('#close-btn')
const sideBar = document.querySelector('aside')

menuBtn.addEventListener('click', ()=>{
    sideBar.style.display = 'block'
})

closeBtn.addEventListener('click', ()=>{
    sideBar.style.display = 'none'
})

const themeBtn = document.querySelector('.theme-btn')

themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');

    themeBtn.querySelector('span:first-child').classList.toggle('active')
    themeBtn.querySelector('span:last-child').classList.toggle('active')
})