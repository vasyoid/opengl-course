#version 410

in vec3 pos;
in vec3 normal;

uniform vec3 lightPos;

out vec4 fragColor;

void main()
{
    // TASK_1: set ambient lighting to 0.1
    float ambient = 0;
    // TASK_2: calculate diffuse lighting
    float diffuse = 0;
    // TASK_3: calculate specular lighting
    float specular = 1;
    float final = ambient + 0.8 * diffuse + 0.4 * specular;
    fragColor = vec4(final, final, final, 1);
}
