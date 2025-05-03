#version 330

in vec3 pos;
out vec4 fragColor;

uniform vec3 u_cam_pos;
uniform vec3 u_sphere_pos;
uniform vec3 u_cube_pos;
uniform vec3 u_cylinder_pos;

float xCylinder(vec3 p)
{
    return 42;
}

float yCylinder(vec3 p)
{
    return 42;
}

float zCylinder(vec3 p)
{
    return 42;
}

float cube(vec3 p)
{
    return 42;
}

float sphere(vec3 p)
{
    return 42;
}

float scene(vec3 p)
{
    return min(min(sphere(p), cube(p)), yCylinder(p));
}

vec3 sceneColor(vec3 p)
{
    return vec3(1, 1, 1);
}

float rayMarch(vec3 origin, vec3 dir)
{
    return 0;
}

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

void main()
{
    vec3 origin = u_cam_pos;
    vec3 dir = pos.xyz - origin;
    dir = normalize(dir);

    float disTravelled = rayMarch(origin, dir);
    vec3 hitPos = origin + disTravelled * dir;
    vec3 n = normal(hitPos);

    if (disTravelled >= 1000)
    {
        fragColor = vec4(0, 0, 0, 1);
    }
    else
    {
        float dotNL = dot(n, normalize(vec3(-1, 1, 1)));
        float diff = max(dotNL, 0.0) * 0.5;

        vec3 viewDir = normalize(origin - hitPos);
        vec3 reflectDir = reflect(-lightDir, n);
        float spec = pow(clamp(dot(viewDir, reflectDir), 0, 1), 32) * 0.2;

        float ambient = 0.15;
        vec3 color = sceneColor(hitPos) * (diff + spec + ambient);
        fragColor = vec4(color, 1);
    }
}