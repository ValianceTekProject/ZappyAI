/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** SpiralIncantationEffect.hpp
*/

#pragma once

#include "AIncantationEffect.hpp"

#include <cmath>
#include <vector>
#include <algorithm>

namespace zappy {
    namespace gui {
        namespace raylib {
            class SpiralIncantationEffect : public AIncantationEffect
            {
                public:
                    SpiralIncantationEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color = BLUE
                    );
                    ~SpiralIncantationEffect() override = default;

                    void update(const float &deltaUnits) override;

                    void render(const Vector3 &position) const override;

                    private:
                        Vector2 _tile;
                        float _animationTime;
                        void _renderSpiralParticles(const Vector3 &center, float progress) const;
                        bool isAt(int x, int y) const;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
