#version 460

in vec3 pos;

out vec4 fragColor;

uniform vec2 shift;
uniform float zoom;

vec2 f(vec2 z, vec2 c)
{
    return vec2(z.x * z.x - z.y * z.y, 2 * z.x * z.y) + c;
}

void main()
{
    int maxIter = 100;
    vec2 c = (pos.xy) / zoom - shift;
    vec2 z = vec2(0, 0);
    int i = 0;
    while (i < maxIter && length(z) < 4)
    {
        z = f(z, c);
        i++;
    }
    float color = min(1.0, i / 100.0);
    fragColor = vec4(color, color, color, 1);
}
