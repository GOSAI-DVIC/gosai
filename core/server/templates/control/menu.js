let modules = {};
let canvas;

const xoffset = -260; // millimeters
const yoffset = 70;

const screenwidth = 392.85; //millimeters
const screenheight = 698.4;

let global_data = {};
let recieved = false;

let img;
let image_size

function preload() {
  img = loadImage('remote/assets/microphone.jpg');
  
}

function setup() {
    canvas = createCanvas(windowWidth, windowHeight);
    image_size = height * 0.1;
    img.resize(image_size, image_size*1.6);
    frameRate(120);
}

function draw() { 
  background(255);
  let app_number = 4;
  
  let head_line     = 0.16 * height; //Note : these are percentages position from top page
  let body          = 0.60 * height;
  let footer_line   = 0.76 * height;
  let big_margin    = 0.04 * height;
  let little_margin = 0.03 * height;
  
  let button_width  = width  * 0.5;
  let button_heigth = (body - 2* (big_margin+little_margin)) / app_number

  let title_size = parseInt((width+height) * 0.05)
  let text_size = parseInt(button_heigth *0.4)
  
  // TITLE
  textSize(title_size)
  textAlign(CENTER, CENTER);
  text("Platform_name", width/2, head_line/2)
  
  //LINE UNDER TITLE
  strokeWeight(parseInt(title_size * 0.05));
  line(0.1*width, head_line, 0.9*width, head_line);
  
  //BUTTONS
  let compt = 1;
  for (let y = head_line + big_margin; y < footer_line - big_margin -1; y += (body - 2* big_margin) / app_number) {
    button = createButton(`App ${compt}`);
    button.position(width/2 - (button_width / 2), y)
    button.size(button_width, button_heigth); //(0.52*height/app_number)-5);
    button.style("font-family", "Bodoni");
    button.style("font-size", `${text_size}px`);
    compt ++;     
  }
  
  //FOOTLINE
  strokeWeight(parseInt(text_size * 0.05));
  line(0.45*width, footer_line, 0.55*width, footer_line);    
  
  //MICROPHONE
  image(img, width/2 - img.width/2, (footer_line + height) / 2 - (img.height/2));
  push()
  noFill();
  circle(width/2, (footer_line + height) / 2, image_size*1.8)
  pop();
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
