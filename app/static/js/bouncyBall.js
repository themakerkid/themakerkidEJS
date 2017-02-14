var sketchProc3 = function (processingInstance) {
    with(processingInstance) {
        size(400, 400);
        frameRate(30);

        // position of the ball
        var y = 0;
        // how far the ball moves every time
        var speed = 6;

        draw = function () {
            background(127, 204, 255); // Background colour

            fill(66, 66, 66); // Colour of the ellipse
            ellipse(200, y, 50, 50); // The actual ellipse

            if (y > 375) { // if statement
                speed = -6; // set the speed to go 6 pixels backwards
            }

            if (y < 25) { // Another if statement
                speed = 6; // set the speed to go 6 pixels forwards
            }

            // move the ball
            y = y + speed;
        };
    }
}