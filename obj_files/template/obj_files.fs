#version 410

in vec3 pos;
in vec3 normal;

// TASK2: add in variable for texture coordinate

uniform vec3 lightPos;
uniform vec3 viewPos;

// TASK2: add uniform texture

out vec4 fragColor;

void main()
{
    float ambient = 0.4;
    vec3 lightDir = normalize(lightPos - pos);

    vec3 norm = normal;
    float diffuse = clamp(dot(norm, lightDir), 0, 1);

    vec3 viewDir = normalize(viewPos - pos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float specular = pow(clamp(dot(viewDir, reflectDir), 0, 1), 16);

    float final = ambient + 0.6 * diffuse + 0.2 * specular;

    // TASK2: multiply texture color by final lighting coefficient
    fragColor = vec4(final, final, final, 1);
}