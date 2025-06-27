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
                ARenderer() : _gameState(nullptr) {}
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
                    const int &x,
                    const int &y
                ) override;
                virtual void addPlayer(const game::Player &player) override;

                virtual void updatePlayerPosition(
                    const int &id,
                    const int &x,
                    const int &y,
                    const game::Orientation &orientation
                ) override;
                virtual void updatePlayerLevel(const int &id, const size_t &level) override;
                virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory) override;

                virtual void playerExpulsion(const int &id) override;

                virtual void playerBroadcast(const int &id, const std::string &message) override;

                virtual void startIncantation(
                    const int &x, const int &y,
                    const int &level,
                    const std::vector<int> &playerIds
                ) override;
                virtual void endIncantation(const int &x, const int &y, const bool &result) override;

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
