class App {
    constructor() {
        this.name = "template_app";
        this.activated = false;
    }

    // Called on the creation of the app by GOSAI
    set(width, height, socket) {
        this.width = width;
        this.height = height;
        this.socket = socket;

        // The app won't be shown until this.activated is set to true
        this.activated = true;
    }

    // Called when the screen is resized
    windowResized() {}

    // Called when the app is paused
    pause() {}

    // Called when the app is resumed
    resume() {}

    // Called on every frame, before show()
    update() {}

    // Called on every frame, after update()
    show() {}
}

export const template_app = new App();
