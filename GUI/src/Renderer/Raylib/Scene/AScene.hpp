/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AScene.hpp
*/

#pragma once

#include "IScene.hpp"
#include "InputManager.hpp"

#include <unordered_map>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AScene : public IScene
            {
                public:
                    AScene();
                    ~AScene() override = default;

                    virtual void init(const std::shared_ptr<game::Map> &map) override;

                    void handleInput() override;


                    virtual void addEgg(const game::Egg &egg);
                    virtual void addPlayer(const game::Player &player);

                    virtual void updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation);
                    virtual void updatePlayerLevel(const int &id, const size_t &level);
                    virtual void updatePlayerInventory(const int &id, const game::Inventory &inventory);

                    virtual void hatchEgg(const int &eggId);

                    virtual void removeEgg(const int &eggId);
                    virtual void removePlayer(const int &id);

                    virtual void endGame(const std::string &teamName);
                protected:
                    std::shared_ptr<game::Map> _map;

                    InputManager _inputManager;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
