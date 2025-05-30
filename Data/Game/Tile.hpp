/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Tile.hpp
*/

#pragma once

#include "ResourceContainer.hpp"

namespace zappy {
    namespace game {
        class Tile : public ResourceContainer {
            public:
                Tile() = default;
                Tile(const Tile &other) = default;
                ~Tile() = default;
        };
    }
}
