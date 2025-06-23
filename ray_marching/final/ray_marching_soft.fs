#version 330

in vec3 pos;
out vec4 fragColor;

uniform vec3 u_cam_pos;
uniform float u_time;
uniform float u_smooth;
uniform float u_sphere_z;
uniform float u_sphere_y;
uniform float u_sphere_r;
uniform float u_mode;

const vec3 cube_pos = vec3(3, 0, 0);

float cube(vec3 p)
{
    vec3 q = abs(p - cube_pos) - 0.5;
    return length(max(q, 0)) + min(max(max(q.x, q.y), q.z), 0);
}

float sphere(vec3 p)
{
    return distance(p, vec3(3, u_sphere_y, u_sphere_z)) - u_sphere_r;
}

float smin(float a, float b, float k)
{
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0, 1);
    return mix(b, a, h) - k * h * (1 - h);
}

float unite(float a, float b)
{
    return smin(a, b, u_smooth);
}

float intersect(float a, float b)
{
    return smin(a, b, -u_smooth);
}

float subtract(float a, float b)
{
    return intersect(a, -b);
}

float scene(vec3 p)
{
    if (u_mode == 1) return unite(cube(p), sphere(p));
    if (u_mode == 2) return intersect(cube(p), sphere(p));
    return subtract(cube(p), sphere(p));
}

vec3 sceneColor(vec3 p)
{
    return vec3(1, 1, 1);
}

float rayMarch(vec3 ro, vec3 rd)
{
    float d = 0.;// total distance travelled
    float cd;// current scene distance
    vec3 p;// current position of ray

    for (int i = 0; i < 1000; ++i)
    { // main loop
        p = ro + d * rd;// calculate new position
        cd = scene(p);// get scene distance

        // if we have hit anything or our distance is too big, break loop
        if (cd < 0.0001 || d >= 1000) break;

        // otherwise, add new scene distance to total distance
        d += cd;
    }

    return d;// finally, return scene distance
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

    // Get ray origin and direction from camera uniforms
    vec3 origin = u_cam_pos;
    vec3 dir = pos.xyz - origin;
    dir = normalize(dir);

    // Ray marching and find total distance travelled
    float disTravelled = rayMarch(origin, dir);// use normalized ray

    // Find the hit position
    vec3 hitPos = origin + disTravelled * dir;

    // Get normal of hit point
    vec3 n = normal(hitPos);

    if (disTravelled >= 1000)
    {
        fragColor = vec4(0, 0, 0, 1);
    }
    else
    {
        vec3 lightDir = normalize(vec3(sin(u_time), 1, cos(u_time)));
        if (rayMarch(hitPos + 0.01 * lightDir, lightDir) < 1000)
        {
            vec3 color = sceneColor(hitPos) * 0.15;
            fragColor = vec4(color, 1);
        }
        else
        {
            float dotNL = dot(n, lightDir);
            float diff = max(dotNL, 0.0) * 0.5;
            vec3 viewDir = normalize(origin - hitPos);
            vec3 reflectDir = reflect(-lightDir, n);
            float spec = pow(clamp(dot(viewDir, reflectDir), 0, 1), 32) * 0.2;

            float ambient = 0.15;
            vec3 color = sceneColor(hitPos) * (diff + spec + ambient);
            fragColor = vec4(color, 1);
        }
    }
}