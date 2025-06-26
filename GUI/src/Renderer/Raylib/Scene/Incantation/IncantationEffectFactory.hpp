/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** IncantationEffectFactory.hpp
*/

#pragma once

#include <memory>
#include <array>

#include "AIncantationEffect.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            enum class IncantationType {
                WAVE,
                INCANTATION_EFFECT_COUNT
            };

            constexpr static size_t INCANTATION_EFFECT_COUNT = static_cast<size_t>(IncantationType::INCANTATION_EFFECT_COUNT);

            class IncantationEffectFactory {
                public:
                    static std::unique_ptr<IIncantationEffect> create(
                        const IncantationType &type,
                        const int &playerId,
                        const float &duration,
                        const Color &color
                    );

                private:
                    static std::unique_ptr<IIncantationEffect> createWave(const int &playerId, const float &duration, const Color &color);

                    // function pointer array
                    using CreateMethod = std::unique_ptr<IIncantationEffect>(*)(const int &, const float &, const Color &);
                    static const std::array<CreateMethod, INCANTATION_EFFECT_COUNT> _createMethods;
            };
        } // namespace raylib
    } // namespace gui
}
