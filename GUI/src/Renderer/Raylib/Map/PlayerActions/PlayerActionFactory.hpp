/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerActionFactory.hpp
*/

#pragma once

#include "PlayerTranslation.hpp"
#include "PlayerRotation.hpp"
#include "PlayerBroadcast.hpp"

#include "EffectFactory.hpp"

#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerActionFactory
            {
                public:
                    PlayerActionFactory() = delete;
                    ~PlayerActionFactory() = delete;

                    static std::shared_ptr<IPlayerAction> createTranslation(
                        const int &playerId,
                        const Translation &translation,
                        std::shared_ptr<IFloor> floor,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );

                    static std::shared_ptr<IPlayerAction> createRotation(
                        const int &playerId,
                        const Rotation &rotation,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );

                    static std::shared_ptr<APlayerAction> createBroadcast(
                        const int &playerId,
                        const BroadcastType &type,
                        const Color &color,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
