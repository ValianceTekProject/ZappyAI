/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Tile.hpp
*/

#pragma once

#include "RessourceContainer.hpp"

namespace zappy {
    namespace game {
        class Tile : public RessourceContainer {
            public:
                Tile() = default;
                Tile(const Tile &other) = default;
                ~Tile() = default;
        };
    }
}
