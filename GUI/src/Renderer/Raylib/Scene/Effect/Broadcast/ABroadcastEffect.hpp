/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ABroadcastEffect.hpp
*/

#pragma once

#include "AEffect.hpp"

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class ABroadcastEffect : public AEffect
            {
                public:
                    ABroadcastEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    );
                    virtual ~ABroadcastEffect() override = default;

                    int _playerId;

                    float _elapsedTime;
                    float _duration;

                    Color _color;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
