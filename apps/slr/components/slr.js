export class Slr{
    constructor(sketch) {
        this.cyan = color(50,250,255);
        this.white = color(255,255,255);
        this.light_red = (240,75,55);
        this.sign;
        this.probability;
        this.sentence = [];
        this.threshold = 0.9;
        
    }

    reset() {}

    update_data(sign, probability) {
        
        if (sign != undefined && probability != undefined) {
            this.sign = sign;
            this.probability = probability;
            if (this.probability > this.threshold && this.sign != "nothing" && this.sign != "empty") {
                if (this.sentence.length > 0) {
                    if (this.sign != this.sentence[this.sentence.length-1]) {
                        this.sentence.push(this.sign);
                    }
                }
                else {
                    this.sentence.push(this.sign);
                }
                    
            }
            if (this.sentence.length > 5) {
                this.sentence.shift();
            }
            
        }
    }

    show(sketch) {
        //Affichage de l'action détectée
        fill(this.cyan);
        noStroke();
        rect(0,60,int(this.probability*100),90);

        textSize(32);
        fill(this.white);
        text(this.sign, 0, 85);

        //Affichage de l'action cible
        // fill(light_red);
        // noStroke();
        // rect(0,560,100,590);

        // textSize(32);
        // fill(white);
        // text(sign, 0, 585);

        //Affichage de la séquence
        fill(this.cyan);
        noStroke();
        rect(0, 0, 640, 40);

        textSize(32);
        fill(this.white);
        // text(this.sentence, 3, 30);
        text(this.sentence, 3, 30);
        
    }
        

    update() {
    }
}