/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Movement.hpp
*/

#pragma once

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            enum class ActionType {
                TRANSLATION,
                ROTATION,
                BROADCAST,
                INCANTATION
            };

            struct Movement {
                int id;
                Vector3 destination;
                Vector3 movementVector;
            };

            using Translation = Movement;
            using Rotation = Movement;
        }
    }
}
