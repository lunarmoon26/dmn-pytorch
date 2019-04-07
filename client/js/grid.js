"use strict";

let board = new Array();
let score = 0;
let hasConflicted = new Array();
let winOnce = false;

let documentWidth = window.screen.width;
let documentHeight = window.screen.height;
//let gridContainerWidth = 0.92*documentWidth;
//let cellSideLength = 0.18*documentWidth;
//let cellSpace = 0.04*documentWidth;
let gridContainerWidth = 400;
let cellSideLength = 100;
let cellSpace = 26;

let GRID_N = 3;

let userLocation = {
    "x": -1,
    "y": -1
};

function newGrid(){
	init();
	generateUser();
}

function init(){
	for(var i=0;i<GRID_N;i++){
		for(var j=0;j<GRID_N;j++){
			var gridCell = $("#grid-cell-"+i+"-"+j);
			gridCell.css("top",getPosTop(i,j));
			gridCell.css("left",getPosLeft(i,j));
		}
	}
	for(var i=0;i<GRID_N;i++){
		board[i] = new Array();
		hasConflicted[i] = new Array();
		for(var j=0;j<GRID_N;j++){
			board[i][j] = {"number": 0};
			hasConflicted[i][j] = false;
		}
	}
	winOnce = false;
	score = 0;
	updateBoardView();
}

function updateBoardView(){
	$(".number-cell").remove();
	for(var i=0;i<GRID_N;i++){
		for(var j=0;j<GRID_N;j++){
			$("#grid-container").append('<div class = "number-cell" id = "number-cell-'+i+'-'+j+'"></div>');
			var theNumberCell = $('#number-cell-'+i+"-"+j);

			if(board[i][j]["number"] == 0){
				theNumberCell.css("width","0px");
				theNumberCell.css("height","0px");
				theNumberCell.css("top",getPosTop(i,j)+cellSideLength/2);
				theNumberCell.css("left",getPosLeft(i,j)+cellSideLength/2);
			}else{
				theNumberCell.css("width",cellSideLength+"px");
				theNumberCell.css("height",cellSideLength+"px");
				theNumberCell.css("top",getPosTop(i,j));
				theNumberCell.css("left",getPosLeft(i,j));
				theNumberCell.css("background-color",getItemCellBgColor(board[i][j]));
				theNumberCell.css("color",getItemCellFontColor(board[i][j]));
//				theNumberCell.css("font-size",getItemCellFontSize(board[i][j]));
				theNumberCell.text(getGridText(board[i][j]));
			}

			hasConflicted[i][j] = false;
		}
	}
	$('.number-cell').css('line-height',cellSideLength+"px");
}

function getPosTop(i,j){
	return cellSpace+i*(cellSpace+cellSideLength);
}

function getPosLeft(i,j){
	return cellSpace+j*(cellSpace+cellSideLength);
}

function generateUser(){
	if(noSpaceInBoard(board)){
		return false;
	}

	var randomX = parseInt(Math.floor(Math.random()*GRID_N));
	var randomY = parseInt(Math.floor(Math.random()*GRID_N));

	while(true){
		if(board[randomX][randomY]["number"] == 0){
			break;
		}
		var randomX = parseInt(Math.floor(Math.random()*GRID_N));
		var randomY = parseInt(Math.floor(Math.random()*GRID_N));
	}

	userLocation = {"x": randomX, "y": randomY};

	var randomNumber = Math.random()<0.5?2:4;

	board[randomX][randomY]["number"] = randomNumber;
	let currentUser = "Tony";
	board[randomX][randomY]["user"] = currentUser;
	showItemWithAnimation(randomX,randomY,currentUser);

	return true;
}

function noSpaceInBoard(board){
	for(var i=0;i<GRID_N;i++){
		for(var j=0;j<GRID_N;j++){
			if(board[i][j]["number"] == 0){
				return false;
			}
		}
	}
	return true;
}

function showItemWithAnimation(randomX,randomY,text){
	var numberCell = $("#number-cell-"+randomX+"-"+randomY);

	numberCell.css("background-color",getItemCellBgColor(board[randomX][randomY]));
	numberCell.css("color",getItemCellFontColor(board[randomX][randomY]));
//	numberCell.css("font-size",getItemCellFontSize(randomNumber));
	numberCell.text(text);

	numberCell.animate({
		width:cellSideLength,
		height:cellSideLength,
		top:getPosTop(randomX,randomY),
		left:getPosLeft(randomX,randomY)
	},100);
}

function showMoveAnimation(fromX,fromY,toX,toY){
	var numberCell = $("#number-cell-"+fromX+"-"+fromY);
	let newTop = getPosTop(toX,toY);
	let newLeft = getPosLeft(toX,toY);
	numberCell.animate({
		top:newTop,
		left:newLeft
	},200);
	updateBoardView();
}

function getItemCellBgColor(item){

//	switch(item["number"]){
//		case 2:return "#eee4da"; break;
//		case 4:return "#ede0c8"; break;
//		case 8:return "#f2b179"; break;
//		case 16:return "#f59563"; break;
//		case 32:return "#f67c5f"; break;
//		case 64:return "#ec6544"; break;
//		case 128:return "#e44d29"; break;
//		case 256:return "#edcf72"; break;
//		case 512:return "#c8a145"; break;
//		case 1024:return "#a8832b"; break;
//		case 2048:return "#86aa9c"; break;
//		case 4096:return "#a6c"; break;
//		case 8192:return "#791e6f"; break;
//	}
//	return "black";
    return "#ede0c8";
}

function getItemCellFontColor(item){
	if(item["number"] <= 4){
		return "#776e65";
	}
	return "white";
}

function getItemCellFontSize(item){
//	if(item["number"] <= 64){
//		return 0.6*cellSideLength+"px";
//	}else if(item["number"] <= 512){
//		return 0.5*cellSideLength+"px";
//	}else if(item["number"] <=8192){
//		return 0.4*cellSideLength+"px";
//	}else{
//		return 0.3*cellSideLength+"px";
//	}
    return 0.6*cellSideLength+"px";
}

function getGridText(item) {
    return item["user"] || "";
}

function nomove(board){
	if(canMoveLeft()||canMoveDown()||canMoveRight()||canMoveUp()){
		return false;
	}
	return true;
}

function canMoveLeft(){
    if (userLocation["y"] === 0) {
	return false;
	} else {
	return true;
	}
}

function canMoveRight(){
	if (userLocation["y"] === GRID_N-1) {
	return false;
	} else {
	return true;
	}
}

function canMoveUp(){
	if (userLocation["x"] === 0) {
	return false;
	} else {
	return true;
	}
}

function canMoveDown(){
	if (userLocation["x"] === GRID_N-1) {
	return false;
	} else {
	return true;
	}
}

function noLeftBlock(i,j,k,board){
	for(var m=k+1;m<j;m++){
		if(board[i][m]["number"]!=0){
			return false;
		}
	}
	return true;
}
function noRightBlock(i,j,k,board){
	for(var m=k-1;m>j;m--){
		if(board[i][m]["number"]!=0){
			return false;
		}
	}
	return true;
}
function noDownBlock(i,j,k,board){
	for(var m=k-1;m>i;m--){
		if(board[m][j]["number"]!=0){
			return false;
		}
	}
	return true;
}
function noUpBlock(i,j,k,board){
	for(var m=k+1;m<i;m++){
		if(board[m][j]["number"]!=0){
			return false;
		}
	}
	return true;
}

$(document).keydown(function (event) {

  switch (event.keyCode) {
	case 37: // left
	  event.preventDefault();
      if(moveLeft()){
//					setTimeout("generateOneNumber()",210);
//					setTimeout("isGameover()",300);
//					setTimeout("isWin()",300);
				}
      break;
    case 38: // up
	  event.preventDefault();
      if(moveUp()){
//					setTimeout("generateOneNumber()",210);
//					setTimeout("isGameover()",300);
//					setTimeout("isWin()",300);
				}
      break;
    case 39: // right
	  event.preventDefault();
      if(moveRight()){
//					setTimeout("generateOneNumber()",210);
//					setTimeout("isGameover()",300);
//					setTimeout("isWin()",300);
				}
      break;
	case 40: // down
	    event.preventDefault();
		if(moveDown()){
//					setTimeout("generateOneNumber()",210);
//					setTimeout("isGameover()",300);
//					setTimeout("isWin()",300);
				}
      break;
    default:
      return;
  }
});

function logRefusedMove(direction){
    log("Cannot move " + direction + ".");
}

function moveLeft() {
    let direction = "left";
    if(!canMoveLeft(board)){
        logRefusedMove(direction);
		return false;
	}
	let newY = userLocation["y"]-1;
	let x = userLocation["x"];
	let y = userLocation["y"];
	board[x][newY]["number"] = board[x][y]["number"];
	board[x][newY]["user"] = board[x][y]["user"];
	board[x][y]["number"] = 0;
	delete board[x][y]["user"];
	showMoveAnimation(x,y,x,newY);
	userLocation["y"] = newY;
    userDirection(direction);
}

function moveUp() {
    let direction = "up";
    if(!canMoveUp(board)){
		logRefusedMove(direction);
		return false;
	}
	let newX = userLocation["x"]-1;
	let x = userLocation["x"];
	let y = userLocation["y"];
	board[newX][y]["number"] = board[x][y]["number"];
	board[newX][y]["user"] = board[x][y]["user"];
	board[x][y]["number"] = 0;
	delete board[x][y]["user"];
	userLocation["x"] = newX;
	showMoveAnimation(x,y,newX,y);
    userDirection(direction);
}

function moveRight() {
    let direction = "right";
    if(!canMoveRight(board)){
		logRefusedMove(direction);
		return false;
	}
	let newY = userLocation["y"]+1;
	let x = userLocation["x"];
	let y = userLocation["y"];
	board[x][newY]["number"] = board[x][y]["number"];
	board[x][newY]["user"] = board[x][y]["user"];
	board[x][y]["number"] = 0;
	delete board[x][y]["user"];
	userLocation["y"] = newY;
	showMoveAnimation(x,y,x,newY);
    userDirection(direction);
}

function moveDown() {
    let direction = "down";
    if(!canMoveDown(board)){
		logRefusedMove(direction);
		return false;
	}
	let newX = userLocation["x"]+1;
	let x = userLocation["x"];
	let y = userLocation["y"];
	board[newX][y]["number"] = board[x][y]["number"];
	board[newX][y]["user"] = board[x][y]["user"];
	board[x][y]["number"] = 0;
	delete board[x][y]["user"];
	userLocation["x"] = newX;
	showMoveAnimation(x,y,newX,y);
    userDirection(direction);
}
