#version 410

in vec3 vPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = vec4(vPos, 1.0);
}
