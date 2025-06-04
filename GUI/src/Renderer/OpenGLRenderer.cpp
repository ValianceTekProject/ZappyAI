/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** OpenGLRenderer.cpp
*/

#include "OpenGLRenderer.hpp"

void zappy::gui::OpenGLRenderer::init()
{
    // Initialize GLEW
    glewExperimental = GL_TRUE;
    glewInit();
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LESS);
    glEnable(GL_BLEND);
}

void zappy::gui::OpenGLRenderer::handleInput()
{
    // Handle input here
}

void zappy::gui::OpenGLRenderer::update()
{

}

void zappy::gui::OpenGLRenderer::render() const
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

bool zappy::gui::OpenGLRenderer::shouldClose() const
{
    return false;
}
