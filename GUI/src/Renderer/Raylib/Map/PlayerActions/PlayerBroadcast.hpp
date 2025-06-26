/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerBroadcast.hpp
*/

#pragma once

#include "APlayerAction.hpp"
#include "BroadcatEffectFactory.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerBroadcast : public APlayerAction {
                public:
                    PlayerBroadcast(
                        const int &playerId,
                        const ActionType &type,
                        std::unique_ptr<IBroadcastEffect> effect,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
                    ~PlayerBroadcast() override = default;

                    void update(const float &deltaUnits, APlayerModel &player) override;
                    void finishAction(const float &deltaUnits, APlayerModel &player) override;

                    bool hasEffectEnded() { return _effect->hasEnded(); }
                    void render(const Vector3 &position);

                private:
                    std::unique_ptr<IBroadcastEffect> _effect;
            };
        }
    }
}
