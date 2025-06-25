/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ITeams
*/

#pragma once

#include "Client.hpp"
#include "ServerInventory.hpp"
#include "ServerPlayer.hpp"
#include <memory>
#include <mutex>
#include <queue>
#include <string>

namespace zappy {
    namespace game {
        class ITeams {

            public:
                virtual std::string getName() const = 0;
                virtual void removePlayer(int playerSocket) = 0;
                virtual const std::vector<std::shared_ptr<ServerPlayer>> &getPlayerList() const = 0;
                virtual void addPlayer(std::shared_ptr<ServerPlayer> player) = 0;
                virtual int getTeamId() const = 0;
        };
    }
}