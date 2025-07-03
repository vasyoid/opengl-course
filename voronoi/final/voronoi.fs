#version 420

uniform vec2 currentPoint;
uniform vec4 currentColor;

uniform float pointsCnt;

layout(std140, binding = 1) uniform PointsUniformBlock {
    vec2 points[256];
};

layout(std140, binding = 2) uniform ColorsUniformBlock {
    vec4 colors[256];
};

in vec2 pos;

out vec4 fragColor;

void main()
{
    float minDist = distance(currentPoint, pos);
    int nearest = -1;
    for (int i = 0; i < pointsCnt; i++) {
        float dist = distance(points[i], pos);
        if (dist < minDist) {
            minDist = dist;
            nearest = i;
        }
    }
    if (minDist < 0.02) {
        fragColor = vec4(0, 0, 0, 1);
    } else if (nearest == -1) {
        fragColor = currentColor;
    } else {
        fragColor = colors[nearest];
    }
}
