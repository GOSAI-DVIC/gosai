let modules = {};
let canvas;

const xoffset = -260; // millimeters
const yoffset = 70;

const screenwidth = 392.85; //millimeters
const screenheight = 698.4;

let global_data = {};
let recieved = false;

let img;
let image_size;
let app_number;
let head_line;
let body;
let footer_line;
let big_margin;
let little_margin;
let button_width;
let button_heigth;
let title_size;
let text_size;

let socket;
let app;
let name_to_buttons = {};
let colors = ["red", "green"]

let platform_name;
let platform_config;

function preload() {
  img = loadImage('remote/assets/microphone.jpg');
  platform_config = loadJSON('/platform/home/config.json');
}

function create_app_button(app) {
  //BUTTONS
  let compt = 0;
  for (let y = head_line + big_margin; y < footer_line - big_margin - 1; y += (body - 2 * big_margin) / app_number) {
    button = createButton(`${app[compt]}`);
    button.position(width / 2 - (button_width / 2), y)
    button.size(button_width, button_heigth); //(0.52*height/app_number)-5);
    button.style("font-family", "Bodoni");
    button.style("font-size", `${text_size}px`);
    button.style("background-color", "red");
    let app_name = app[compt];
    button.mousePressed(() => {socket.emit("start_application", {"application_name" : app_name})});
    name_to_buttons[app[compt]] = button
    compt++;
  }
}

function update_app_button(app_name, flag) {
  name_to_buttons[app_name].style("background-color", colors[flag]);
  if (flag == 1){
    name_to_buttons[app_name].mousePressed(() => {socket.emit("stop_application", {"application_name" : app_name})});
  }
  else {
    name_to_buttons[app_name].mousePressed(() => {socket.emit("start_application", {"application_name" : app_name})});
  }
}

function setup() {
  platform_name = platform_config.name;
  socket.emit("get_available_applications");
  socket.emit("get_started_applications")
  canvas = createCanvas(windowWidth, windowHeight);
  image_size = height * 0.1;
  img.resize(image_size, image_size * 1.6);
  frameRate(120);

  app_number = 4;
  head_line = 0.16 * height; //Note : these are percentages position from top page
  body = 0.60 * height;
  footer_line = 0.76 * height;
  big_margin = 0.04 * height;
  little_margin = 0.03 * height;
  button_width = width * 0.5;
  button_heigth = (body - 2 * (big_margin + little_margin)) / app_number
  title_size = parseInt((width + height) * 0.05)
  text_size = parseInt(button_heigth * 0.4)
}

function draw() {
  background(255);


  // TITLE
  textSize(title_size)
  textAlign(CENTER, CENTER);
  text(`${platform_name}`, width / 2, head_line / 2)

  //LINE UNDER TITLE
  strokeWeight(parseInt(title_size * 0.05));
  line(0.1 * width, head_line, 0.9 * width, head_line);



  //FOOTLINE
  strokeWeight(parseInt(text_size * 0.05));
  line(0.45 * width, footer_line, 0.55 * width, footer_line);

  //MICROPHONE
  image(img, width / 2 - img.width / 2, (footer_line + height) / 2 - (img.height / 2));
  push()
  noFill();
  circle(width / 2, (footer_line + height) / 2, image_size * 1.8)
  pop();
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}