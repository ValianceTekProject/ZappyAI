/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Inventory.hpp
*/

#pragma once

#include "ResourceContainer.hpp"

namespace zappy {
    namespace game {
        class Inventory : public ResourceContainer {
            public:
                Inventory() = default;
                Inventory(const Inventory &other) = default;
                ~Inventory() = default;
        };
    }
}
