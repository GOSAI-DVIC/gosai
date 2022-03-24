let modules = {};
let canvas;

const xoffset = -260; // millimeters
const yoffset = 70;

const screenwidth = 392.85; //millimeters
const screenheight = 698.4;

let global_data = {};
let recieved = false;

let bgcolor
let buttons = [];
let app_number = 5;

function setup() {
    canvas = createCanvas(windowWidth, windowHeight);
    bgcolor = color(200)
    frameRate(120);

    // //inspiration : https://editor.p5js.org/chauw196/sketches/2nBcRRdex
    // for(let y = 10; y <= height-10; y+=20){
    //       // this is a temporary variable
    //       let b = {
    //         diameter: 20,
    //         x: x,
    //         y: y,
    //         on: false
    //       }
        
    //     // push our latest button to the array 
    //     buttons.push(b)
    // }
}


function draw() { 
    
    background(bgcolor); 
        
    // Use color() function 
    let c = color('green'); 
    
    // Use fill() function to fill color 
    fill(c); 
        
    // // Draw a rectangle 
    // button(CENTER)
    // translate(width / 2, height / 2);
    // rect(0, 0, 300, 200); 

    button = createButton(`width = ${width}`);
    button.mouseClicked(changeColor);
    button.position(width / 2 - button.width - 10, height / 2 - button.height);
    button.style("font-family", "Bodoni");
    button.style("font-size", "48px");

    console.log(width)
    console.log(height)

        
}

function mousePressed(){

  
    // loop through the buttons array to check distance
    for(let i = 0; i < buttons.length; i++){
      
      // check the distance between the cursor and the current button
      if(dist(mouseX,mouseY,buttons[i].x,buttons[i].y) < buttons[i].diameter/2){
        
      // toggle the boolean value
      buttons[i].on = !buttons[i].on;
    }
      
    }
  }

function changeColor() {
    bgcolor = color(random(255))
}


function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
