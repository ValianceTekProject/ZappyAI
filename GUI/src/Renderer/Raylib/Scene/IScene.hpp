/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IScene.hpp
*/

#pragma once

#include "IPlayerModel.hpp"
#include "IFloor.hpp"
#include "InputManager.hpp"

#include "GameState.hpp"

#include "raylib.h"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IScene
            {
                public:
                    virtual ~IScene() = default;

                    virtual void init() = 0;

                    virtual Camera &getCamera() = 0;
                    virtual const Camera &getCamera() const = 0;

                    virtual void handleInput(InputManager &inputManager) = 0;
                    virtual void update() = 0;

                    virtual void render() const = 0;

                    virtual bool shouldClose() const = 0;

                    virtual void addEgg(const int &eggId) = 0;
                    virtual void addPlayer(const int &id) = 0;

                    virtual void updatePlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation) = 0;
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
        } // namespace raylib
    } // namespace gui
} // namespace zappy
