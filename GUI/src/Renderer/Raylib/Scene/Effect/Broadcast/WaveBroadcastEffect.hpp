/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** WaveBroadcastEffect.hpp
*/

#pragma once

#include "ABroadcastEffect.hpp"

#include <vector>
#include <algorithm>

namespace zappy {
    namespace gui {
        namespace raylib {
            struct Pulse {
                float radius;
                float elapsed;
            };

            class WaveBroadcastEffect : public ABroadcastEffect
            {
                public:
                    WaveBroadcastEffect(
                        const int &playerId,
                        const float &duration,
                        const Color &color = BLUE
                    );
                    ~WaveBroadcastEffect() override = default;

                    void update(const float &deltaUnits) override;

                    void render(const Vector3 &position) const override;

                    bool hasEnded() const override;

                private:
                    std::vector<Pulse> _pulses;
                    float _pulseTimer;

                    constexpr static float PULSE_INTERVAL = 2.0f;  // relancer un cercle toutes les 0.5 unités
                    constexpr static float PULSE_SPEED = 3.0f;     // vitesse de propagation
                    constexpr static float PULSE_LIFETIME = 3.0f;  // durée de vie de chaque cercle
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
