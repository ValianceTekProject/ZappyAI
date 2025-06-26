/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** PlayerIncantation.hpp
*/

#pragma once

#include "APlayerAction.hpp"
#include "IncantationEffectFactory.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerIncantation : public APlayerAction {
                public:
                    PlayerIncantation(
                        const int &playerId,
                        const ActionType &type,
                        std::unique_ptr<IIncantationEffect> effect,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
                    ~PlayerIncantation() override = default;

                    void update(const float &deltaUnits, APlayerModel &player) override;
                    void finishAction(APlayerModel &player) override;

                    void render(const Vector3 &position);

                private:
                    std::unique_ptr<IIncantationEffect> _effect;
            };
        }
    }
}
