/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** IncantationEffect.hpp
*/

#pragma once

#include "AIncantationEffect.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IncantationEffect : public AIncantationEffect
            {
                public:
                    IncantationEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color = BLUE
                    );
            };
        }
    }
}