/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.hpp
*/

#pragma once

#include "GameMap.hpp"

namespace gui {
    class GameState
    {
        public:
            GameState() = default;
            ~GameState() = default;

        private:
            GameMap _map;
    };
}
