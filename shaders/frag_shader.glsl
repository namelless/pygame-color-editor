#version 330 core

uniform vec3 ratios;
uniform sampler2D tex;

in vec2 uvs;
out vec4 frag_color;

void main(){
    vec4 color = texture(tex, uvs);
    frag_color = vec4(color.rgb * ratios,color.a);
}