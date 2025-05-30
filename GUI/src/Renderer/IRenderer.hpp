/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IRenderer.hpp
*/

#pragma once

#include "GameState.hpp"

#include <iostream>
#include <memory>

namespace zappy {
    namespace gui {
        class IRenderer
        {
            public:
                virtual ~IRenderer() = default;

                virtual void init() = 0;

                virtual void setGameState(std::shared_ptr<game::GameState> gameState) = 0;

                virtual void handleInput() = 0;
                virtual void update() = 0;

                virtual void render() const = 0;

                virtual bool shouldClose() const = 0;
        };
    }
}
