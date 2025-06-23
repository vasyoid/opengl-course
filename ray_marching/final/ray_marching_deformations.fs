#version 330

in vec3 pos;
out vec4 fragColor;

uniform vec3 u_cam_pos;
uniform float u_time;
uniform float u_mode;
uniform float u_smooth;

float cube(vec3 p)
{
    vec3 q = abs(p) - 0.5;
    return length(max(q, 0)) + min(max(max(q.x, q.y), q.z), 0);
}

vec3 sceneColor(vec3 p)
{
    return vec3(1, 1, 1);
}

float corners(float d, float r) {
    return d - r;
}

vec3 repeat_x(vec3 p, float a, float b) {
    return vec3(a + mod(p.x - a, b - a), p.yz);
}

vec3 repeat_z(vec3 p, float a, float b) {
    return vec3(p.xy, a + mod(p.z - a, b - a));
}

vec3 twist(vec3 p) {
    p.y -= 1;
    float t = (p.y + 2.5) * sin(u_smooth);
    return vec3(p.x * cos(t) - p.z * sin(t),
                p.y / 2,
                p.x * sin(t) + p.z * cos(t));
}

float scene(vec3 p)
{
    if (u_mode == 1) {
        return corners(cube(p), u_smooth);
    }
    if (u_mode == 2) {
        return cube(repeat_x(repeat_z(p, -0.7, 0.7), -0.7, 0.7));
    }
    if (u_mode == 3) {
        return cube(twist(p));
    }
    return cube(p);
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
        if (cd < 0.001 || d >= 1000) break;

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
        vec3 lightDir = normalize(vec3(sin(u_time), 1, cos(u_time)));
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