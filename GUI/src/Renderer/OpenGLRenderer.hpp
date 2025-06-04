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
                OpenGLRenderer() = default;
                ~OpenGLRenderer() = default;

                void init() override;

                void setGameState(std::shared_ptr<game::GameState> gameState) override
                    { _gameState = gameState; }

                void handleInput() override;
                void update() override;

                void render() const override;

                bool shouldClose() const override;

            private:
                std::shared_ptr<game::GameState> _gameState;

                GLuint _program;
        };
    }
}
