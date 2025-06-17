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

                virtual void addEgg(
                    const int &eggId,
                    const int &fatherId,
                    const int &x,
                    const int &y
                ) = 0;
                virtual void addPlayer(const game::Player &player) = 0;

                virtual void updatePlayerPosition(
                    const int &id,
                    const int &x,
                    const int &y,
                    const game::Orientation &orientation
                ) = 0;
                virtual void updatePlayerLevel(const int &id, const size_t &level) = 0;
                virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory) = 0;

                virtual void PlayerExpulsion(const int &id) = 0;

                virtual void PlayerBroadcast(const int &id, const std::string &message) = 0;

                virtual void StartIncantation(
                    const int &x, const int &y,
                    const int &level,
                    const std::vector<int> &playerIds
                ) = 0;
                virtual void EndIncantation(const int &x, const int &y, const bool &result) = 0;

                virtual void hatchEgg(const int &eggId) = 0;

                virtual void removeEgg(const int &eggId) = 0;
                virtual void removePlayer(const int &id) = 0;

                virtual void endGame(const std::string &teamName) = 0;
        };
    }
}
