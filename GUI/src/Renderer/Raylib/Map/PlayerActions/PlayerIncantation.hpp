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
                        const Vector2 &pos,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    ) : APlayerAnimAction(animationId, playerId, type, std::move(effect), timeUnit, elapsedTime), _pos(pos) {}
                    ~PlayerIncantation() override = default;

                    const Vector2 &getPosition() const { return _pos ;}

                private:
                    Vector2 _pos;
            };
        }
    }
}
