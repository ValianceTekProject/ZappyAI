/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** APlayerAction.hpp
*/

#pragma once

#include "IPlayerAction.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class APlayerAction : public IPlayerAction
            {
                public:
                    APlayerAction(
                        const int &playerId,
                        const ActionType &actionType,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
                    virtual ~APlayerAction() override = default;

                    int getPlayerId() const override { return playerId; }
                    ActionType getActionType() const override { return actionType; }

                    virtual void update(const float &deltaUnits, APlayerModel &player) override;

                    virtual bool ActionWillEnd(const float &deltaUnits) const override;
                    virtual void finishAction(APlayerModel &player) override = 0;

                protected:
                    int playerId;

                    ActionType actionType;

                    float _timeUnit;
                    float _elapsedTime;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
