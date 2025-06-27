#version 420

uniform vec2 currentPoint;
uniform vec4 currentColor;

uniform float pointsCnt;

layout(packed, binding = 1) uniform PointsUniformBlock {
    vec2 points[256];
};

layout(std140, binding = 2) uniform ColorsUniformBlock {
    vec4 colors[256];
};

in vec2 pos;

out vec4 fragColor;

void main()
{
    float minDist = 10;
    int nearest = 0;
    // 1. Найти номер ближайшей к данному пикселю точки и расстояние до нее
    // 4. Учесть текущую точку (currentPoint и currentColor) при вычислении ближайшей точки
    //    и при выборе цвета пикселя
    fragColor = colors[nearest];
}
