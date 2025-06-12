/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** InputManager.cpp
*/

#include "InputManager.hpp"

/**
 * @brief Updates the state of keyboard keys in the input manager
 *
 * This method iterates through existing key states and updates their status based on current key press conditions.
 * It handles key state transitions between PRESSED, HELD, RELEASED, and NONE states.
 * Additionally, it detects newly pressed keys not currently tracked and adds them to the key states map.
 */
void zappy::gui::raylib::InputManager::update()
{
    for (auto &[key, state] : _keyStates) {
        if (IsKeyDown(key)) {
            state = (state == KeyState::PRESSED || state == KeyState::HELD)
                ? KeyState::HELD : KeyState::PRESSED;
        } else {
            state = (state == KeyState::PRESSED || state == KeyState::HELD)
                ? KeyState::RELEASED : KeyState::NONE;
        }
    }

    int key = GetKeyPressed();
    while (key != KEY_NULL) {
        if (_keyStates.find(key) == _keyStates.end())
            _keyStates[key] = KeyState::PRESSED;
        key = GetKeyPressed();
    }
}

/**
 * @brief
 *
 * @param key
 * @return zappy::gui::raylib::InputManager::KeyState
 */
zappy::gui::raylib::InputManager::KeyState zappy::gui::raylib::InputManager::getKeyState(int key) const
{
    auto it = _keyStates.find(key);
    if (it != _keyStates.end())
        return it->second;
    return KeyState::NONE;
}
