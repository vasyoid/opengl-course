#version 410

in vec3 pos;
in vec3 normal;

uniform vec3 lightPos;
uniform vec3 viewPos;

out vec4 fragColor;

void main()
{
    float ambient = 0.1;
    vec3 lightDir = normalize(lightPos - pos);

    vec3 norm = normal;
    float diffuse = clamp(dot(norm, lightDir), 0, 1);

    vec3 viewDir = normalize(viewPos - pos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float specular = pow(clamp(dot(viewDir, reflectDir), 0, 1), 16);

    float final = ambient + 0.8 * diffuse + 0.4 * specular;

    fragColor = vec4(final, final, final, 1);
}