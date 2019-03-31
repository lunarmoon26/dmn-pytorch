"use strict";

let USER_ID = "dummy";
let BASE_URL = "http://localhost:5000";
let ASK_API = "/api/ask";
let ACTION_API = "/api/action";

function userDirection(item) {
    log("Move: " + item);

    let url = BASE_URL + ACTION_API;
    let data = {
        "user_id": USER_ID,
        "action": item
    };

    $.ajax({
    type: "POST",
    url: url,
    data: data,
    crossDomain: true,
    success: function(result) {console.log(result);},
    error: function(result) {console.log("[error]", result);}
    });
}

function submitQuestion() {
    let question = $("#userQuestion").val();
    log("Question: " + question);
    clearUserInput();

    let url = BASE_URL + ASK_API;
    let data = {
        "user_id": USER_ID,
        "question": question
    };

    $.ajax({
    type: "POST",
    url: url,
    data: data,
    crossDomain: true,
    success: function(result) {
        console.log(result);
        log("Answer: " + result["answer"])
    },
    error: function(result) {
        console.log("[error]", result);
        log("Error: " + result["answer"])
    }
    });
}

function clearUserInput() {
    $("#userQuestion").val("");
}

function log(message) {
    $("#conversationLog").append(message + "\n");
}
