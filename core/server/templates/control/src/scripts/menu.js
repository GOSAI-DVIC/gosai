let modules = {};
let canvas;

const xoffset = -260; // millimeters
const yoffset = 70;

const screenwidth = 392.85; //millimeters
const screenheight = 698.4;

let mic_img;
let mic_coords;
let spk_img;
let spk_coords;

let image_size;
let app_number;

let name_to_buttons = {};
let colors = ["Thistle", "SpringGreen", "black"];
let micro = false; //micro state
let micro_start = false;
let speaker = false; //speaker state
let speaker_start = false;
let speaker_request = false;
let angle = 0;
let radius = 125;

let mobileDevice = false;

let platform_name;
let platform_config;

let mic, recorder, soundFile;
var audio = new Audio("./control/src/assets/mySound.mp3");
audio.onended = function () {
    speaker_start = false;
    speaker_request = false;
};

function preload() {
    mic_img = loadImage("./control/src/assets/microphone.jpg");
    spk_img = loadImage("./control/src/assets/speaker.jpg");
    platform_config = loadJSON("./platform/home/config.json");
}

function setup() {
    if (platform_config.name != undefined) {
        platform_name =
            platform_config.name[0].toUpperCase() +
            platform_config.name.substring(1);

        document.getElementById("title").innerHTML = platform_name;
    }

    socket.emit("core-app_manager-get_available_applications");
    socket.emit("core-app_manager-get_started_applications");

    canvas = createCanvas(windowWidth * 0.9, min(windowWidth * 0.35, 750 * 0.35));
    canvas.parent("canvas-div");

    angleMode(DEGREES);
    imageMode(CENTER);
    frameRate(120);

    image_size = min(height * 0.4, 100);

    mic_coords = {
        x: (2 * width) / 6,
        y: height / 2,
    };

    spk_coords = {
        x: (4 * width) / 6,
        y: height / 2,
    };

    // // create an audio in
    // mic = new p5.AudioIn();
    // // users must manually enable their browser microphone for recording to work properly!
    // mic.start();
    // // create a sound recorder
    // recorder = new p5.SoundRecorder();
    // // connect the mic to the recorder
    // recorder.setInput(mic);
    // // create an empty sound file that we will use to playback the recording
    // soundFile = new p5.SoundFile();
}

function windowResized() {
    resizeCanvas(windowWidth * 0.9, min(windowWidth * 0.35, 750 * 0.35));
    image_size = min(height * 0.4, 100);

    mic_coords = {
        x: (2 * width) / 6,
        y: height / 2,
    };

    spk_coords = {
        x: (4 * width) / 6,
        y: height / 2,
    };
}

function draw() {
    background(0);

    //MICROPHONE
    push();
    stroke(214, 128, 255);
    strokeWeight(3);
    image(mic_img, mic_coords.x, mic_coords.y, image_size, 1.6 * image_size);
    noFill();
    circle(mic_coords.x, mic_coords.y, image_size * 1.8);

    if (
        mouseIsPressed &&
        dist(mouseX, mouseY, mic_coords.x, mic_coords.y) < image_size * 0.9
    ) {
        micro = true;

        let x = radius * cos(angle);
        let y = radius * sin(angle);
        strokeWeight(image_size * 0.1);
        stroke(151, 130, 255);
        circle(mic_coords.x, mic_coords.y, image_size * 1.9);
        stroke(128, 191, 255);
        arc(
            mic_coords.x,
            mic_coords.y,
            image_size * 2.1,
            image_size * 2.1,
            270 + x,
            90 + y
        );
    } else {
        micro = false;
    }
    pop();

    // if (micro && !micro_start) {
    //     recorder.record(soundFile)
    //     micro_start = true
    // }
    // if (!micro && micro_start) {
    //     recorder.stop();
    //     saveSound(soundFile,'mySound.wav');
    //     micro_start = false;
    // }

    //SPEAKER
    push();
    stroke(214, 128, 255);
    strokeWeight(3);
    image(spk_img, spk_coords.x, spk_coords.y, 1.6 * image_size, 1.6 * image_size);
    noFill();
    circle(spk_coords.x, spk_coords.y, image_size * 1.8);

    if (
        (mouseIsPressed &&
            dist(mouseX, mouseY, spk_coords.x, spk_coords.y) <
            image_size * 0.9) ||
        speaker_request
    ) {
        speaker = true;
        speaker_start = true;
        speaker_button();
        let x = radius * cos(angle);
        let y = radius * sin(angle);
        noFill();
        strokeWeight(image_size * 0.1);
        stroke(151, 130, 255);
        circle(spk_coords.x, spk_coords.y, image_size * 1.9);
        stroke(128, 191, 255);
        arc(
            spk_coords.x,
            spk_coords.y,
            image_size * 2.1,
            image_size * 2.1,
            270 + x,
            90 + y
        );
    } else {
        speaker = false;
    }
    if (!speaker && speaker_start) {
        stop_audio();
    }
    pop();
    angle++;
}

function isMobileDevice() {
    var check = false;
    (function (a) {
        if (
            /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(
                a
            ) ||
            /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(
                a.substr(0, 4)
            )
        )
            check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    // console.log(check)
    return check;
}

function create_app_button(applications_list) {
    //BUTTONS
    if (Object.keys(name_to_buttons).length > 0) return;
    app_number = applications_list.length;
    for (let i = 0; i < app_number; i++) {
        let app_name = applications_list[i]["name"];
        button = createButton(
            app_name[0].toUpperCase() + app_name.substring(1)
        );
        button.parent("buttons-div");
        button.class("app-button");
        button.mousePressed(() => {
            socket.emit("core-app_manager-start_application", {
                application_name: app_name,
            });
        });
        name_to_buttons[app_name] = button;
    }
}

function update_app_button(app_name, flag) {
    name_to_buttons[app_name].style("background-color", colors[flag]);
    if (flag == 1) {
        name_to_buttons[app_name].mousePressed(() => {
            socket.emit("core-app_manager-stop_application", {
                application_name: app_name,
            });
        });
    } else {
        name_to_buttons[app_name].mousePressed(() => {
            socket.emit("core-app_manager-start_application", {
                application_name: app_name,
            });
        });
    }
}

function speaker_button() {
    audio.play();
}

function stop_audio() {
    audio.pause();
}
