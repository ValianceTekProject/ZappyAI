/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AScene.hpp
*/

#pragma once

#include "IScene.hpp"
#include "MapRenderer.hpp"

#include <memory>
#include <unordered_map>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AScene : public IScene
            {
                public:
                    AScene(const std::shared_ptr<game::GameState> &gameState);
                    ~AScene() override = default;

                    virtual void init() override;

                    Camera &getCamera() override { return _camera; }
                    const Camera &getCamera() const override { return _camera; }

                    virtual void handleInput(InputManager &inputManager) override;
                    virtual void update() override;

                    virtual void addEgg(const int &id) override;
                    virtual void addPlayer(const int &id) override;

                    virtual void updatePlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation) override;
                    virtual void updatePlayerLevel(const int &id, const size_t &level) override;
                    virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory) override;

                    virtual void PlayerExpulsion(const int &id) override;

                    virtual void PlayerBroadcast(const int &id, const std::string &message) override;

                    virtual void StartIncantation(
                        const int &x, const int &y,
                        const int &level,
                        const std::vector<int> &playerIds
                    ) override;
                    virtual void EndIncantation(const int &x, const int &y, const bool &result) override;

                    virtual void hatchEgg(const int &id) override;

                    virtual void removeEgg(const int &id) override;
                    virtual void removePlayer(const int &id) override;

                protected:
                    Camera _camera;

                    const std::shared_ptr<game::GameState> _gameState;

                    const std::unique_ptr<MapRenderer> _mapRenderer;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
