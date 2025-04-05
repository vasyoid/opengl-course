#version 330

in vec3 pos;
out vec4 fragColor;

vec3 normal(vec3 p)
{
    vec3 n = vec3(0, 0, 0);
    vec3 e;
    for (int i = 0; i < 4; i++)
    {
        e = 0.5773 * (2.0 * vec3((((i + 3) >> 1) & 1), ((i >> 1) & 1), (i & 1)) - 1.0);
        n += e * scene(p + e * 0.001);
    }
    return normalize(n);
}

float rayMarch(origin, direction) {
    return 1000.0;
}

void main()
{

    // Get ray origin and direction from camera uniforms
    vec3 origin = vec3(0, 0, -2);
    vec3 direction = pos.xyz - origin;
    direction = normalize(direction);

    // Ray marching and find total distance travelled
    float dist = rayMarch(origin, direction);// use normalized ray

    // Find the hit position
    vec3 hp = origin + dist * direction;

    // Get normal of hit point
    vec3 n = normal(hp);

    if (dist >= 1000)
    { // if ray doesn't hit anything
        fragColor = vec4(0, 0, 0, 1);
    }
    else
    { // if ray hits something
        // Calculate Diffuse model
        float dotNL = dot(n, vec3(2, 2, 0));
        float diff = max(dotNL, 0.0) * 0.5;
        float spec = pow(diff, 16) * 3;
        float ambient = 0.15;

        vec3 color = vec3(1, 1, 1) * (spec + ambient + diff);
        fragColor = vec4(color, 1);// color output
    }
}