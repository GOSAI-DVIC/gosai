import * as THREE from "/gosai/libs/three/build/three.module.js";

class App {
    constructor() {
        this.name = "template_app";
        this.z_index = 10;
        this.activated = false;
    }

    set(width, height, socket) {
        this.width = width;
        this.height = height;
        this.socket = socket;

        this.canvasElement = document.createElement('canvas');
        this.canvasElement.width = width;
        this.canvasElement.height = height;
        this.canvasElement.style.position = 'absolute';
        this.canvasElement.style.left = '0px';
        this.canvasElement.style.top = '0px';
        this.canvasElement.style.zIndex = this.z_index;

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvasElement,
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(this.renderer.domElement);

        this.scene = new THREE.Scene();

        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(0, 0, 10);
        this.camera.lookAt(0, 0, 0);
        this.scene.add(this.camera);

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
    show() {
        this.renderer.render(this.scene, this.camera);
    }
}


export const template_app = new App();
