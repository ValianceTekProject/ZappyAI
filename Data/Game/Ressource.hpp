/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Ressource.hpp
*/

#pragma once

#include <iostream>

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

        const std::string names[COUNT];
        const std::string &getName(Ressource res);
        Ressource getRessource(const std::string &name);
    }
}
