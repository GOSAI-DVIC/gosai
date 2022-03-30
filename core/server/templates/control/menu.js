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

let app;
let name_to_buttons = {};
let colors = ["Thistle", "SpringGreen", "black"]
let micro = false;
let angle = 0;
let radius = 125;
let x;
let y;

let mobileDevice = false;

let platform_name;
let platform_config;

function preload() {
    img = loadImage('./control/assets/microphone.jpg');
    platform_config = loadJSON('./platform/home/config.json');
}

function setup() {
    angleMode(DEGREES);
    mobileDevice = isMobileDevice()
    platform_name = platform_config.name;
    platform_name = platform_name[0].toUpperCase()+ platform_name.substring(1)
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
    title_size = parseInt((width + height) * 0.04)
    text_size = parseInt(button_heigth * 0.4)
}

function draw() {
    background(0);

    // TITLE
    noStroke()
    textSize(title_size * 0.9)
    textAlign(CENTER, CENTER);
    fill(128, 191, 255);
    text(`${platform_name}`, width / 2, head_line / 2)

    // Powered by Gosai
    textSize(title_size * 0.2)
    textAlign(CENTER, CENTER);
    fill(151, 130, 255);
    text(`Powered by GOSAI`, width / 2, head_line * 0.85)

    //LINE UNDER TITLE
    strokeWeight(parseInt(title_size * 0.05));
    stroke(214, 128, 255);
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



    if (mouseIsPressed && (dist(mouseX, mouseY, width / 2, (footer_line + height) / 2) < image_size * 0.9)) {
        micro = true;
        x = radius * cos(angle);
        y = radius * sin(angle);
        push()
        noFill();
        strokeWeight(image_size * 0.1)
        stroke(151, 130, 255)
        circle(width / 2, (footer_line + height) / 2, image_size * 1.9)
        stroke(128, 191, 255);
        arc(width / 2, (footer_line + height) / 2, image_size * 2.1, image_size * 2.1, 270 + x, 90 + y);
        pop();
    } else {
        micro = false;
    }
    angle++;
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}

function isMobileDevice() {
    var check = false;
    (function (a) {
        if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    // console.log(check)
    return check;
};

function create_app_button(app) {
    //BUTTONS
    let compt = 0;
    for (let y = head_line + big_margin; y < footer_line - big_margin - 1; y += (body - 2 * big_margin) / app_number) {
        button = createButton(`${app[compt][0].toUpperCase()+app[compt].substring(1)}`);
        button.position(width / 2 - (button_width / 2), y)
        button.size(button_width, button_heigth); //(0.52*height/app_number)-5);
        button.style("border", colors[2])
        button.style("font-family", "Bodoni");
        button.style("font-size", `${text_size}px`);
        button.style("background-color", colors[0]);
        let app_name = app[compt];
        button.mousePressed(() => {
            socket.emit("start_application", {
                "application_name": app_name
            })
        });
        name_to_buttons[app[compt]] = button
        compt++;
    }
}

function update_app_button(app_name, flag) {
    name_to_buttons[app_name].style("background-color", colors[flag]);
    if (flag == 1) {
        name_to_buttons[app_name].mousePressed(() => {
            socket.emit("stop_application", {
                "application_name": app_name
            })
        });
    } else {
        name_to_buttons[app_name].mousePressed(() => {
            socket.emit("start_application", {
                "application_name": app_name
            })
        });
    }
}
