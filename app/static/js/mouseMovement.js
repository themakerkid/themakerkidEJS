var sketchProc2 = function (processingInstance) {
    with(processingInstance) {

        size(400, 350);
        frameRate(30);
        mouseMoved = function() {
            fill(mouseX, mouseX, mouseY);
            stroke(mouseY, mouseY, mouseX);
            ellipse(mouseX, mouseY, mouseY, mouseY);
        };



    }
};