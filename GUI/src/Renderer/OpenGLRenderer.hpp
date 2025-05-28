/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** OpenGLRenderer.cpp
*/

#pragma once

#include "IRenderer.hpp"

#include <GL/glew.h>

namespace zappy {
    namespace gui {
        class OpenGLRenderer : public IRenderer
        {
            public:
                OpenGLRenderer();
                ~OpenGLRenderer();

                void init() override;

                void handleInput() override;
                void update() override;

                void render() override;

                void close() override;

            private:
                GLuint _program;
        };
    }
}
