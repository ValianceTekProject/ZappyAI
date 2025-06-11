/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** RaylibRenderer.hpp
*/

#pragma once

#include "ARenderer.hpp"

#include "IScene.hpp"

namespace zappy {
    namespace gui {
        class RaylibRenderer : public ARenderer {
            public:
                RaylibRenderer();
                ~RaylibRenderer() override = default;

                void init() override;
                void handleInput() override;
                void update() override;
                void render() const override;
                bool shouldClose() const override;

                void addEgg(const int &eggId, const int &fatherId, const size_t &x, const size_t &y) override;
                void addPlayer(const game::Player &player) override;

                void updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation) override;
                void updatePlayerLevel(const int &id, const size_t &level) override;
                void updatePlayerInventory(const int &id, const game::Inventory &inventory) override;

                void hatchEgg(const int &eggId) override;
                void removeEgg(const int &eggId) override;
                void removePlayer(const int &id) override;

                void endGame(const std::string &teamName) override;

            private:
                std::unique_ptr<raylib::IScene> _scene;
        };
    }
}
