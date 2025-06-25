/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ATeams
*/

#pragma once

#include "ITeams.hpp"

namespace zappy {
    namespace game {

        class ATeams : public ITeams {

            public:
                ATeams(const std::string &name, int id) : _name(name), _teamId(id) {}

                std::string getName() const { return _name; }

                void addPlayer(std::shared_ptr<ServerPlayer> player);
                void removePlayer(int playerSocket);

                const std::vector<std::shared_ptr<ServerPlayer>> &getPlayerList() const;

                int getTeamId() const {return this->_teamId;}

            private:
                const std::string _name;
                int _teamId;
                std::vector<std::shared_ptr<ServerPlayer>> _playerList;
                std::mutex _playerListLock;
        };
    }
}