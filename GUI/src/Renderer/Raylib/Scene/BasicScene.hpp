/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicScene (minimal implementation)
*/

#pragma once

#include "AScene.hpp"

#include <raylib.h>
#include <unordered_map>

namespace zappy {
    namespace gui {
        namespace raylib {
            class BasicScene : public AScene {
                public:
                    BasicScene(const std::shared_ptr<game::GameState> &gameState);
                    ~BasicScene() override = default;

                    void init() override;

                    void handleInput(InputManager &inputManager);

                    void update() override;
                    void render() const override;

                    bool shouldClose() const override;

                    void addEgg(const int &id) override;

                    void addPlayer(const int &id) override;

                    void updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation) override;
                    void updatePlayerLevel(const int &id, const size_t &level) override;
                    void updatePlayerInventory(const int &id, const game::Inventory &inventory) override;

                    void hatchEgg(const int &eggId) override;

                    void removeEgg(const int &eggId) override;

                    void removePlayer(const int &id) override;

                    void endGame(const std::string &teamName) override;

                private:
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
