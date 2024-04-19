#version 330

in vec3 pos;

out vec4 fragColor;

vec2 f(vec2 z, vec2 c)
{
    return vec2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + c;
}


void main()
{
    fragColor = vec4(1, 1, 1, 1);
}
