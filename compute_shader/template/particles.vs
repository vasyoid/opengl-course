#version 430

uniform float pTime;

layout (location = 0) in vec2 vPos;
layout (location = 1) in vec4 pPosSize;
layout (location = 2) in vec4 pColor;

out vec2 texCoord;
out vec4 color;

void main()
{
    vec2 pPos = pPosSize.xy;
    float pSize = pPosSize.z;
    // 1. Set gl_Position, texCoord and color
}
