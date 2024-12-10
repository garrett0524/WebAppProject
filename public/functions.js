const ws = true;
let socket = null;

function initWS() {
    // Establish a WebSocket connection with the server
    socket = new WebSocket('ws://' + window.location.host + '/websocket');

    // Called whenever data is received from the server over the WebSocket connection
    socket.onmessage = function (ws_message) {

        const message = JSON.parse(ws_message.data);
        const messageType = message.messageType
        if(messageType === 'chatMessage'){
            addMessageToChat(message);

        }
        else if(messageType == 'AdduserList'){
            adduser_tolist(message);
        }
        else if(messageType == 'DeluserList'){
            remUser_fromlist(message);
        }
        else{
            // send message to WebRTC
            processMessageAsWebRTC(message, messageType);
        }

    }
}

function deleteMessage(messageId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(this.response);
        }
    }
    request.open("DELETE", "/chat-messages/" + messageId);
    request.send();
}

function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id;
    let messageHTML = "<br><button onclick='deleteMessage(\"" + messageId + "\")'>X</button> ";
    messageHTML += "<span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    return messageHTML;
}

function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}

function userMessageHTML(messageJSON) {
    const username = messageJSON.username;
    return "<div>" + username + "</div>";
}


function adduser_tolist(messageJSON) {
    const userlist = document.getElementById("UserList");
    const usernameToAdd = messageJSON.username;
    const userItems = userlist.getElementsByTagName("div");

    // Check if username is already in the list
    for (let i = 0; i < userItems.length; i++) {
        const userItem = userItems[i];
        const username = userItem.innerText.trim(); // Get the username text and remove  extra whitespace

        // If the username is already in the list then return and dont do any adding
        if (username === usernameToAdd) {
            return;
        }
    }

    // If the username is not in the list, add it
    userlist.innerHTML += userMessageHTML(messageJSON);
}

function remUser_fromlist(messageJSON) {
    const usernameToRemove = messageJSON.username;
    const userList = document.getElementById("UserList");
    const userItems = userList.getElementsByTagName("div");

    // Loop through the user items in the user list
    for (let i = 0; i < userItems.length; i++) {
        const userItem = userItems[i];
        const username = userItem.innerText.trim(); // Get the username text and trim any extra whitespace

        // Check if the username matches the one to remove
        if (username === usernameToRemove) {
            // Remove the user item from the user list
            userItem.remove();
            break; // Exit the loop after removing the user item
        }
    }
}

function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const message = chatTextBox.value;
    chatTextBox.value = "";
    if (ws) {
        // Using WebSockets
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
        // socket.send(JSON.stringify({'messageType': 'chatMessage', 'message': message}));
    } else {
        // Using AJAX
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                console.log(this.response);
            }
        }
        const messageJSON = {"message": message};

        const xsrfToken = document.getElementById('xsrf-token').value;

        request.open("POST", "/chat-messages");
        request.setRequestHeader("X-XSRF-Token", xsrfToken); // Include the token
        request.send(JSON.stringify(messageJSON));
    }
    chatTextBox.focus();
}

function updateChat() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/chat-messages");
    request.send();
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });


    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😀";
    document.getElementById("chat-text-box").focus();

    updateChat();

    if (ws) {
        initWS();
    } else {
        const videoElem = document.getElementsByClassName('video-chat')[0];
        videoElem.parentElement.removeChild(videoElem);
        setInterval(updateChat, 5000);
    }

    // use this line to start your video without having to click a button. Helpful for debugging
    // startVideo();
}