/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IScene.hpp
*/

#pragma once

#include "IPlayerModel.hpp"
#include "IFloor.hpp"
#include "GameState.hpp"

#include "raylib.h"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IScene
            {
                public:
                    virtual ~IScene() = default;

                    virtual void init(const std::shared_ptr<game::Map> &map) = 0;

                    virtual void update() = 0;
                    virtual void render() const = 0;

                    virtual void handleInput() = 0;

                    virtual bool shouldClose() const = 0;

                    virtual void addEgg(const game::Egg &egg) = 0;
                    virtual void addPlayer(const game::Player &player) = 0;

                    virtual void updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation) = 0;
                    virtual void updatePlayerLevel(const int &id, const size_t &level) = 0;
                    virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory) = 0;

                    virtual void hatchEgg(const int &eggId) = 0;

                    virtual void removeEgg(const int &eggId) = 0;
                    virtual void removePlayer(const int &id) = 0;

                    virtual void endGame(const std::string &teamName) = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
