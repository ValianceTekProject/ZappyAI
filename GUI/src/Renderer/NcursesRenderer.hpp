/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NcursesRenderer.cpp
*/

#pragma once

#include "ARenderer.hpp"

#include <ncurses.h>
#include <sstream>

namespace zappy {
    namespace gui {
        class NcursesRenderer : public ARenderer
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

                bool shouldClose() const override;

                void endGame(const std::string &teamName) override;

            private:
                void _initWindow();
                void _initColors();

                void _drawMap() const;
                void _drawTile(
                    const game::Tile &tile,
                    const std::vector<game::Egg> &eggs,
                    const std::vector<game::Player> &players,
                    size_t x, size_t y,
                    size_t row, size_t col
                ) const;

                std::shared_ptr<game::GameState> _gameState;
                bool _shouldClose;

                WINDOW *_window;

                bool _help;
        };
    }
}
