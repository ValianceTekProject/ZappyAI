/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** PlayerIncantation.hpp
*/

#pragma once

#include "APlayerAnimAction.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerIncantation : public APlayerAnimAction {
                public:
                    PlayerIncantation(
                        const ssize_t &animationId,
                        const int &playerId,
                        const ActionType &type,
                        std::unique_ptr<IEffect> effect,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    ) : APlayerAnimAction(animationId, playerId, type, std::move(effect), timeUnit, elapsedTime) {}
                    ~PlayerIncantation() override = default;
            };
        }
    }
}
