/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ARenderer.hpp
*/

#pragma once

#include "IRenderer.hpp"
#include "GuiError.hpp"

#include <memory>

namespace zappy {
    namespace gui {
        class ARenderer : public IRenderer {
            public:
                ARenderer() = default;
                virtual ~ARenderer() override = default;

                virtual void init() override = 0;

                void setGameState(std::shared_ptr<game::GameState> gameState) override
                    { _gameState = gameState; }

                virtual void handleInput() override = 0;
                virtual void update() override = 0;

                virtual void render() const override = 0;

                virtual bool shouldClose() const override = 0;

                virtual void addEgg(
                    const int &eggId,
                    const int &fatherId,
                    const size_t &x,
                    const size_t &y
                ) override;
                virtual void addPlayer(const game::Player &player) override;

                virtual void updatePlayerPosition(
                    const int &id,
                    const size_t &x,
                    const size_t &y,
                    const game::Orientation &orientation
                ) override;
                virtual void updatePlayerLevel(const int &id, const size_t &level) override;
                virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory) override;

                virtual void hatchEgg(const int &eggId) override;

                virtual void removeEgg(const int &eggId) override;
                virtual void removePlayer(const int &id) override;

                virtual void endGame(const std::string &teamName) override;

            protected:
                void _checkGameState() const;

                std::shared_ptr<game::GameState> _gameState;
        };
    }
}
