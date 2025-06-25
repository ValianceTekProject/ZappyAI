/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** TeamGui
*/

#pragma once

#include "ATeams.hpp"

namespace zappy {
    namespace game {
        class ServerPlayer;
        class TeamsGui : public ATeams {
           public:
            TeamsGui(const std::string &name, int id) : ATeams(name, id) {}

            ~TeamsGui() = default;

           private:
        };
    }  // namespace game
}  // namespace zappy