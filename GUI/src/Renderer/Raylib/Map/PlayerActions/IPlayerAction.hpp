/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IPlayerAction.hpp
*/

#pragma once

#include "Movement.hpp"
#include "APlayerModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IPlayerAction
            {
                public:
                    virtual ~IPlayerAction() = default;

                    virtual int getPlayerId() const = 0;
                    virtual ActionType getActionType() const = 0;

                    virtual bool hasActionStarted() const = 0;
                    virtual void startAction() = 0;

                    virtual void update(const float &deltaUnits, APlayerModel &player) = 0;

                    virtual bool ActionWillEnd(const float &deltaUnits) const = 0;
                    virtual void finishAction(const float &deltaUnits, APlayerModel &player) = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
