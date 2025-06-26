/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** EffectFactory.hpp
*/

#pragma once

#include "IEffect.hpp"
#include "WaveBroadcastEffect.hpp"
#include "SpiralIncantationEffect.hpp"

#include <memory>
#include <array>

namespace zappy {
    namespace gui {
        namespace raylib {
            enum class EffectType {
                WAVE_BROADCAST,
                EFFECT_COUNT
            };

            constexpr static size_t EFFECT_COUNT = static_cast<size_t>(EffectType::EFFECT_COUNT);

            class EffectFactory {
                public:
                    static std::unique_ptr<IEffect> create(
                        const EffectType &type,
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    );

                private:
                    static std::unique_ptr<IEffect> createWave(const int &playerId, const float &duration, const Color &color);
                    static std::unique_ptr<IEffect> createIncantation(const int &playerId, const float &duration, const Color &color);

                    // function pointer array
                    using CreateMethod = std::unique_ptr<IEffect> (*)(const int &, const float &, const Color &);
                    static const std::array<CreateMethod, EFFECT_COUNT> _createMethods;
            };
        } // namespace raylib
    } // namespace gui
}
