/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** WaveIncantationEffect.hpp
*/

#pragma once

#include "AIncantationEffect.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class WaveIncantationEffect : public AIncantationEffect
            {
                public:
                    WaveIncantationEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color = BLUE
                    );
                    ~WaveIncantationEffect() override = default;

                    void update(const float &deltaUnits) override;

                    void render(const Vector3 &position) const override;

                private:
                    float _radius;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
