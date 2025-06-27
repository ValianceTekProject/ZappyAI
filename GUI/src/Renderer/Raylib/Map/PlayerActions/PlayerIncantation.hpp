/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** PlayerIncantation.hpp
*/

#pragma once

#include "APlayerAnimAction.hpp"
#include "AIncantationEffect.hpp"

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

                    void incantationResult(const bool &res)
                    {
                        AIncantationEffect &effect = static_cast<AIncantationEffect &>(*_effect);
                        effect.incantationResult(res);
                    };

                private:
                    Vector2 _pos;
            };
        }
    }
}
