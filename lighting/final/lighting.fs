#version 410

in vec3 pos;
in vec3 normal;

uniform vec3 lightPos;
uniform vec3 viewPos;

uniform int u_ambient;
uniform int u_diffuse;
uniform int u_specular;

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

    float final = u_ambient * ambient + u_diffuse * 0.8 * diffuse + u_specular * 0.4 * specular;

    fragColor = vec4(final, final, final, 1);
}