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
            enum class MovementType {
                TRANSLATION,
                ROTATION
            };

            struct Movement {
                int id;
                MovementType type;
                Vector3 destination;
                Vector3 movementVector;
                int timeUnits;
                float elapsedTime;
            };
        }
    }
}
