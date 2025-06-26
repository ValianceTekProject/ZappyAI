/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** AIncantationEffect.hpp
*/

#pragma once

#include "IIncantationEffect.hpp"

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AIncantationEffect : public IIncantationEffect
            {
                public:
                    AIncantationEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    );
                    virtual ~AIncantationEffect() = default;

                    virtual void update(const float &deltaUnits);
                    virtual void render(const Vector3 &position) const = 0;

                    virtual bool isFinished() const;

                protected:
                    int _playerId;

                    float _elapsedTime;
                    float _duration;

                    Color _color;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
