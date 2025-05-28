/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.hpp
*/

#pragma once

#include "Map.hpp"

namespace zappy {
    namespace game {
        class GameState
        {
            public:
                GameState() = default;
                ~GameState() = default;

            private:
                game::Map _map;
        };
    }
}
