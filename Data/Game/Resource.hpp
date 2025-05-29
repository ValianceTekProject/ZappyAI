/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Resource.hpp
*/

#pragma once

#include "GameError.hpp"

#include <array>

namespace zappy {
    namespace game {
        enum class Resource {
            FOOD = 0,
            LINEMATE = 1,
            DERAUMERE = 2,
            SIBUR = 3,
            MENDIANE = 4,
            PHIRAS = 5,
            THYSTAME = 6,
            RESOURCE_SIZE
        };

        const size_t RESOURCE_QUANTITY = static_cast<size_t>(Resource::RESOURCE_SIZE);

        const std::array<std::string, RESOURCE_QUANTITY> names = {
            "food",
            "linemate",
            "deraumere",
            "sibur",
            "mendiane",
            "phiras",
            "thystame"
        };

        size_t castResource(const Resource &res);
        const std::string &getName(Resource &res);
        Resource getResource(const std::string &name);
    }
}
