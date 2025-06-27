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

                    void incantationResult(const bool &res)
                    {
                        this->_color = res ? GREEN : RED;
                        constexpr float elapsedTime = 0.f;
                        constexpr float duration = 10.f;

                        this->_elapsedTime = elapsedTime;
                        this->_duration = duration;
                    }
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
