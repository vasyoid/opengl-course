#version 330

in vec3 vPos;

out vec3 pos;

void main()
{
    gl_Position = vec4(vPos, 1.0);
    pos = vPos;
}
