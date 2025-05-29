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
        enum class Ressource {
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

        const std::array<float, static_cast<int> (Ressource::COUNT) - 1> coeff = {
            0.5,
            0.3,
            0.15,
            0.1,
            0.1,
            0.08,
            0.05
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
