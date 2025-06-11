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
            class AScene : public IScene {
            public:
                AScene();
                ~AScene() override = default;

                virtual void init(const std::shared_ptr<game::Map> &map) override;

                void handleInput() override;

            protected:
                std::shared_ptr<game::Map> _map;

                InputManager _inputManager;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
