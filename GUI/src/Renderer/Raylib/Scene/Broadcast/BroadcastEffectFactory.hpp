/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BroadcastEffectFactory.hpp
*/

#pragma once

#include "WaveBroadcastEffect.hpp"

#include <memory>
#include <array>

namespace zappy {
    namespace gui {
        namespace raylib {
            enum class BroadcastType {
                WAVE,
                BROADCAST_EFFECT_COUNT
            };

            constexpr static size_t BROADCAST_EFFECT_COUNT = static_cast<size_t>(BroadcastType::BROADCAST_EFFECT_COUNT);

            class BroadcastEffectFactory {
                public:
                    static std::unique_ptr<IBroadcastEffect> create(const BroadcastType &type, const int &playerId, const float &duration, const Color &color);

                private:
                    static std::unique_ptr<IBroadcastEffect> createWave(const int &playerId, const float &duration, const Color &color);

                    // function pointer array
                    using CreateMethod = std::unique_ptr<IBroadcastEffect>(*)(const int &, const float &, const Color &);
                    static const std::array<CreateMethod, BROADCAST_EFFECT_COUNT> _createMethods;
            };
        } // namespace raylib
    } // namespace gui
}
