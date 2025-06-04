/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.hpp
*/

#pragma once

#include "Map.hpp"
#include "Player.hpp"

namespace zappy {
    namespace game {
        class GameState
        {
            public:
                GameState() : _frequency(100) {}
                ~GameState() = default;

                void setFrequency(const size_t &frequency) { _frequency = frequency; }
                void initMap(const size_t &width, const size_t &height) { _map.init(width, height); }

                size_t getFrequency() const { return _frequency; }

                void updateTile(const size_t &x, const size_t &y, Tile &tile) { _map.setTile(x, y, tile); }

                void addTeam(const std::string &teamName) { _teams.push_back(teamName); }

                void addEgg(
                    const int &eggId,
                    const int &playerId,
                    const size_t &x,
                    const size_t &y
                );
                void addPlayer(Player &player) { _players.push_back(player); }

                void updatePlayerPosition(
                    const int &id,
                    const size_t &x,
                    const size_t &y,
                    const Orientation &orientation
                );
                void updatePlayerLevel(const int &id, const size_t &level);
                void updatePlayerInventory(const int &id, const Inventory &inventory);

                void hatchEgg(const int &eggId);

                void removeEgg(const int &eggId);
                void removePlayer(const int &id);

                Player &getEggById(const int &eggId);
                Player &getPlayerById(const int &id);

                void endGame(const std::string &teamName);

            private:
                std::vector<Player &> getPlayersByCoord(const size_t &x, const size_t &y);

                size_t _frequency;

                std::vector<Player> _players;
                std::vector<std::string> _teams;

                game::Map _map;
        };
    }
}
