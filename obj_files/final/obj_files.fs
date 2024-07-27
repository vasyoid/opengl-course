#version 410

in vec3 pos;
in vec3 normal;
in vec2 texCoord;

uniform vec3 lightPos;
uniform vec3 viewPos;

uniform sampler2D tex;

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

    fragColor = vec4(texture(tex, texCoord).xyz * final, 1);
}