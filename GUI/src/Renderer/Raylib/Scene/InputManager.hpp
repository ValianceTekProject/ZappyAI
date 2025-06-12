/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** InputManager.hpp
*/

#pragma once

#include <raylib.h>

#include <unordered_map>

namespace zappy {
    namespace gui {
        namespace raylib {
            class InputManager {
                public:
                    enum class KeyState {
                        NONE,
                        PRESSED,
                        HELD,
                        RELEASED
                    };

                    void update();
                    KeyState getKeyState(int key) const;

                private:
                    std::unordered_map<int, KeyState> _keyStates;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
