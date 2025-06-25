/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ABroadcastEffect.hpp
*/

#pragma once

#include "IBroadcastEffect.hpp"

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class ABroadcastEffect : public IBroadcastEffect
            {
                public:
                    ABroadcastEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    );
                    virtual ~ABroadcastEffect() = default;

                    virtual bool isFinished() const;
                    virtual void update(const float &deltaUnits);

                    virtual void render() const = 0;

                protected:
                    int _playerId;

                    float _elapsedTime;
                    float _duration;

                    Color _color;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
