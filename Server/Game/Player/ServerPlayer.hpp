//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <chrono>

#include "Client.hpp"
#include "Player.hpp"
#include "ITeams.hpp"

namespace zappy {
    namespace game {
        class ITeams;

        class ServerPlayer : public Player {

           public:
            ServerPlayer(zappy::server::Client user,
                 size_t id,
                 size_t x,
                 size_t y,
                 Orientation orientation,
                 zappy::game::ITeams &team,
                 size_t level = 1
                )
                : Player::Player(id, x, y, orientation, level),
                _user(std::move(user)),
                _startTime(std::chrono::steady_clock::now()),
                _lifeTime(std::chrono::steady_clock::now()),
                _team(team) {
                    constexpr int startFood = 10;
                    this->collectRessource(zappy::game::Resource::FOOD, startFood);
                }

            ~ServerPlayer() = default;

            zappy::server::Client &getClient() {return this->_user;};

            void startChrono() { _startTime = std::chrono::steady_clock::now(); }

            std::chrono::duration<double> getChrono() const {
                auto now = std::chrono::steady_clock::now();
                return now - _startTime;
            }
            std::chrono::duration<double> getLifeChrono() const {
                auto now = std::chrono::steady_clock::now();
                return now - _lifeTime;
            }
            void resetLifeChrono() { _lifeTime = std::chrono::steady_clock::now(); }

            bool isInAction() { return _actionStarted; }
            void setInAction(bool status) { _actionStarted = status; }
            zappy::game::ITeams &getTeam() { return _team; }


           private:
            zappy::server::Client _user;
            std::chrono::steady_clock::time_point _startTime;
            std::chrono::steady_clock::time_point _lifeTime;

            bool _actionStarted = false;
            zappy::game::ITeams &_team;
        };
    }
}
