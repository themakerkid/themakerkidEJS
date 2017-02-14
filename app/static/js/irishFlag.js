var sketchProc3 = function (processingInstance) {
    with(processingInstance) {
        size(400, 350);
        frameRate(30);
        
        background(9, 5, 59);
        draw = function() {
            fill(0, 255, 0); // green
            rect(mouseX, mouseY, 25, 50);
            fill(255, 255, 255); // white
            rect(mouseX + 25, mouseY, 25, 50);
            fill(255, 187, 0); // orange
            rect(mouseX + 50, mouseY, 25, 50);
        };

    }
};