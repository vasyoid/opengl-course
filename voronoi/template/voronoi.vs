#version 420

uniform float ratio;

in vec2 vPos;

out vec2 pos;

void main()
{
    gl_Position = vec4(vPos, 0.0, 1.0);
    pos = vPos;
    if (ratio > 1) {
        pos.x *= ratio;
    } else {
        pos.y /= ratio;
    }
}
