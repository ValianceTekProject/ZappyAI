/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** WaveBroadcastEffect.hpp
*/

#pragma once

#include "ABroadcastEffect.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
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

                    void render() const override;

                private:
                    float _radius;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
