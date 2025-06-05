/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NcursesRenderer.cpp
*/

#pragma once

#include "IRenderer.hpp"

#include <ncurses.h>

namespace zappy {
    namespace gui {
        class NcursesRenderer : public IRenderer
        {
            public:
                NcursesRenderer();
                ~NcursesRenderer() = default;

                void init() override;

                void setGameState(std::shared_ptr<game::GameState> gameState) override
                    { _gameState = gameState; }

                void handleInput() override;
                void update() override;

                void render() const override;

                bool shouldClose() const override { return _shouldClose; }

            private:
                std::shared_ptr<game::GameState> _gameState;
                bool _shouldClose;

                WINDOW *_window;
        };
    }
}
