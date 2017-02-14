var sketchProc4 = function (processingInstance) {
    with(processingInstance) {
        size(400, 350);
        frameRate(30);
        
        background(245, 204, 204);
        noStroke();
        var draw = function () {
            fill(mouseY, mouseY, mouseX);
            ellipse(mouseX, mouseY, 10, 10);
        };
    }
};