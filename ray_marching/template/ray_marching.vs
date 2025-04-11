#version 330

in vec3 vPos;
out vec3 pos;

uniform mat4 view_inv;

void main()
{
    gl_Position = vec4(vPos, 1.0);
    pos = (view_inv * vec4(vPos, 1.0)).xyz;
}
