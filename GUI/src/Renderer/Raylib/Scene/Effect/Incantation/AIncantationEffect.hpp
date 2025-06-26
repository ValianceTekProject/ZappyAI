/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** AIncantationEffect.hpp
*/

#pragma once

#include "AEffect.hpp"

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AIncantationEffect : public AEffect
            {
                public:
                    AIncantationEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    ) : AEffect::AEffect(playerId, duration, color) {}
                    virtual ~AIncantationEffect() = default;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
