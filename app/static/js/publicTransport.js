var sketchProc2 = function(processingInstance) {
    with(processingInstance) {
        size(400, 400);
        frameRate(30);
        
        var xPos = 10; // start position
        var wheelDist = 74;

        draw = function() {
            background(124, 207, 126);
            // top of the train
            fill(230, 255, 0);
            arc(xPos + 36, 132, 14, 77, 182, 360);
            // a wheel
            line(0, 215, 400, 215);
            fill(0, 0, 0);
            ellipse(xPos, 200, 30, 30);
            fill(255, 255, 255);
            ellipse(xPos, 200, 10, 10);
            // another wheel
            fill(0, 0, 0);
            ellipse(xPos + wheelDist, 200, 30, 30);
            fill(255, 255, 255);
            ellipse(xPos + wheelDist, 200, 10, 10);
            // body of train
            rect(xPos - 14, 132, wheelDist + 28, 52);
            // windows
            rect(xPos - 5, 146, 20, 20);
            line(xPos + 5, 146, xPos + 5, 165);
            line(xPos - 5, 156, xPos + 15, 156);
            rect(xPos + 26, 146, 20, 20);
            rect(xPos + 59, 146, 20, 20);
            
            // Funnel
            rect(xPos + 59, 91, 19, 41);
            // move 2 pixels to the right
            xPos += 2;
            // for looping purposes only
            if (xPos > 400) {
                xPos = -100;
            }
        };

    }
};