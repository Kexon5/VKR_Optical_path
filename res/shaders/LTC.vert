#version 330

layout (location = 0) in vec3 position;
layout (location = 1) in vec4 color;

out vec4 ourColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec4 color_vec;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    if (color_vec.w == 0.5)
    	ourColor = color_vec;
    else
	ourColor = color;
}