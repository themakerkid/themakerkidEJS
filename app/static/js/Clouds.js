var sketchProc = function (processingInstance) {
    with(processingInstance) {

        size(400, 400);
        frameRate(30);


        noStroke();
        var leftX = 170;
        var rightX = 262;
        var sunRadius = 100;

        var draw = function () {
            background(184, 236, 255);

            fill(255, 170, 0);
            ellipse(200, 100, sunRadius, sunRadius);

            sunRadius += 2;

            // clouds 
            fill(255, 255, 255);
            // left cloud
            ellipse(leftX, 150, 126, 97);
            ellipse(leftX + 62, 150, 70, 60);
            ellipse(leftX - 62, 150, 70, 60);

            // right cloud
            ellipse(rightX, 100, 126, 97);
            ellipse(rightX + 62, 100, 70, 60);
            ellipse(rightX - 62, 100, 70, 60);

            leftX--;
            rightX++;
            
            // loop the animation
            if (sunRadius > 250) {
                leftX = 170;
                rightX = 262;
                sunRadius = 100;
            }
        };


    }
};