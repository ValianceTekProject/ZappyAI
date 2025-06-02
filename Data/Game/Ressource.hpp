/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Ressource.hpp
*/

#pragma once

#include <iostream>
#include <vector>
#include <array>

namespace zappy {
    namespace game {
        enum class Resource {
            FOOD,
            LINEMATE,
            DERAUMERE,
            SIBUR,
            MENDIANE,
            PHIRAS,
            THYSTAME,
            NONE,
            COUNT
            
        };

        const std::vector<std::string> names = {
            "food",
            "linemate",
            "deraumere",
            "sibur",
            "mendiane",
            "phiras",
            "thystame"
        };

        const std::string &getName(Resource res);
        Resource getRessource(const std::string &name);
    }
}
