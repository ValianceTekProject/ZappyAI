/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Inventory.hpp
*/

#pragma once

#include "RessourceContainer.hpp"

namespace zappy {
    namespace game {
        class Inventory : public RessourceContainer {
            public:
                Inventory() = default;
                Inventory(const Inventory &other) = default;
                ~Inventory() = default;
        };
    }
}
