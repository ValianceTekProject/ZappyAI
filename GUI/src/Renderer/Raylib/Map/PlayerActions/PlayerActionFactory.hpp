/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerActionFactory.hpp
*/

#pragma once

#include "PlayerActions/IPlayerAction.hpp"
#include "PlayerTranslation.hpp"
#include "PlayerRotation.hpp"
#include "PlayerBroadcast.hpp"
#include "PlayerIncantation.hpp"

#include "EffectFactory.hpp"

#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            constexpr static int FORWARD_TIME = 7;
            constexpr static int ROTATION_TIME = 7;
            constexpr static int EXPULSION_TIME = 1;
            constexpr static int BROADCAST_TIME = 7;
            constexpr static int INCANTATION_TIME = 300;
            constexpr static int NO_ANIMATION = 0;

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

                    static std::shared_ptr<IPlayerAction> createBroadcast(
                        const int &playerId,
                        const EffectType &type,
                        const Color &color,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );

                    static std::shared_ptr<IPlayerAction> createIncantation(
                        const int &playerId,
                        const EffectType &type,
                        const Color &color,
                        const Vector2 &pos,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );

                private:
                    static ssize_t _newId;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
