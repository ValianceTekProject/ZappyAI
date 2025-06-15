/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** InputManager.hpp
*/

#pragma once

#include <raylib.h>

#include <unordered_map>
#include <vector>
#include <functional>

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

                    KeyState getMouseButtonState(int button) const;
                    bool isMouseButtonPressed(int button) const;

                    Vector2 getMouseDelta() const { return _mouseDelta; }
                    Vector2 getMousePosition() const { return _lastMousePosition; }

                private:
                    void _updateState(
                        std::unordered_map<int, KeyState> &states,
                        const std::function<bool(int)> &isDownFn
                    );

                    std::unordered_map<int, KeyState> _keyStates;
                    std::unordered_map<int, KeyState> _mouseButtonStates;

                    Vector2 _lastMousePosition = {0.0f, 0.0f};
                    Vector2 _mouseDelta = {0.0f, 0.0f};
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
