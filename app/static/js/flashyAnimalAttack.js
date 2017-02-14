var sketchProc4 = function (processingInstance) {
    with(processingInstance) {
        size(400, 400);
        frameRate(30);

        var bodyX = 200;
        var bodyY = 220;
        var bodyW = 118;
        var bodyH = bodyW / 2;
        var colours = [[255, 0, 0], [0, 0, 0]];
        var index = 0;

        draw = function () {

            stroke(0, 0, 0);
            background(207, 254, 255);
            fill(240, 209, 36);
            rect(bodyX - 30, bodyY - 20, 18, 110); // the
            rect(bodyX + 10, bodyY - 20, 18, 110); // legs

            rect(109, 205, 70, 20, 10); // the
            rect(217, 205, 70, 20, 10); // arms

            ellipse(bodyX, bodyY, bodyW, 106); // body?
            ellipse(bodyX, bodyY - 70, bodyH, 47); // face?

            if (index === 0) {
                fill(255, 0, 0);
                index = 1;
            } else {
                fill(58, 214, 34);
                index = 0;
            }
            ellipse(186, 145, 10, 10); // the
            ellipse(212, 145, 10, 10); // eyes

            noFill();
            arc(200, 156, 26, 17, -2, 178); // the mouth

            fill(201, 197, 197);
            noStroke();
            triangle(229, 119, 233, 94, 249, 108); // the
            rect(230, 58, 167, 55, 30); // speech bubble

            fill(255, 0, 0);
            textSize(22);
            text("You will die!", 247, 94); // what the animal is saying
        };

    }
};