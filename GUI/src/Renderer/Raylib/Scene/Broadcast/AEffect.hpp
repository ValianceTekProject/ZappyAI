/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AEffect.hpp
*/

#pragma once

#include "IEffect.hpp"

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AEffect : public IEffect
            {
                public:
                    AEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    );
                    virtual ~AEffect() override = default;

                    virtual void update(const float &deltaUnits) override;

                    virtual void render(const Vector3 &position) const override = 0;

                    virtual bool hasEnded() const override;

                protected:
                    int _playerId;

                    float _elapsedTime;
                    float _duration;

                    Color _color;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
