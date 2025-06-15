/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AScene.hpp
*/

#pragma once

#include "IScene.hpp"

#include <unordered_map>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AScene : public IScene
            {
                public:
                    AScene();
                    ~AScene() override = default;

                    virtual void init(const std::shared_ptr<game::GameState> &gameState) override;

                    virtual void handleInput(InputManager &inputManager) override;

                    virtual void addEgg(const int &eggId) override;
                    virtual void addPlayer(const int &id) override;

                    virtual void updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation) override;
                    virtual void updatePlayerLevel(const int &id, const size_t &level) override;
                    virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory) override;

                    virtual void hatchEgg(const int &eggId) override;

                    virtual void removeEgg(const int &eggId) override;
                    virtual void removePlayer(const int &id) override;

                    virtual void endGame(const std::string &teamName) override;

                protected:
                    std::shared_ptr<game::GameState> _gameState;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
