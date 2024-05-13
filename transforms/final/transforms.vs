#version 410

layout (location = 0) in vec3 vPos;
layout (location = 1) in vec3 vColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 color;

void main()
{
    gl_Position = projection * view * model * vec4(vPos, 1.0);
    color = vColor;
}
