/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** APlayerAnimAction.hpp
*/

#pragma once

#include "PlayerActions/APlayerAction.hpp"
#include "PlayerActions/Movement.hpp"
#include "IEffect.hpp"
#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            class APlayerAnimAction : public APlayerAction {
                public:
                    APlayerAnimAction(
                        const int &playerId,
                        const ActionType &actionType,
                        std::unique_ptr<IEffect> effect,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
                    virtual ~APlayerAnimAction() override = default;

                    bool hasEffectEnded() { return _effect->hadEnded(); }

                    virtual void render(const Vector3 &position) = 0;

                protected:
                    std::unique_ptr<IEffect> _effect;
            };
        }
    }
}