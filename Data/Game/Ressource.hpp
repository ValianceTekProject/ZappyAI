/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Ressource.hpp
*/

#pragma once

#include <iostream>
#include <vector>

namespace zappy {
    namespace game {
        enum Ressource {
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

        const std::string &getName(Ressource res);
        Ressource getRessource(const std::string &name);
    }
}
