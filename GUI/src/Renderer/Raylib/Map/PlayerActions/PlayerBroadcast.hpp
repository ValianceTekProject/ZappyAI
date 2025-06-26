/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerBroadcast.hpp
*/

#pragma once

#include "APlayerAnimAction.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerBroadcast : public APlayerAnimAction {
                public:
                    PlayerBroadcast(
                        const int &playerId,
                        const ActionType &type,
                        std::unique_ptr<IEffect> effect,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    ) : APlayerAnimAction(playerId, type, std::move(effect), timeUnit, elapsedTime) {}
                    ~PlayerBroadcast() override = default;
            };
        }
    }
}
