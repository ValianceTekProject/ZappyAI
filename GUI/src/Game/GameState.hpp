/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.hpp
*/

#pragma once

#include "Map.hpp"
#include "Player.hpp"

#include <memory>

namespace zappy {
    namespace game {
        class GameState
        {
            public:
                GameState() : _frequency(100) {}
                ~GameState() = default;

                void setFrequency(const size_t &frequency) { this->_frequency = frequency; }
                void initMap(const size_t &width, const size_t &height) { this->_map = std::make_shared<Map>(width, height); }

                size_t getFrequency() const { return this->_frequency; }

                std::shared_ptr<Map> getMap() { return this->_map; }
                const std::shared_ptr<Map> &getMap() const { return this->_map; }
                const Tile &getTile(const size_t &x, const size_t &y) const { return this->_map->getTile(x, y); }

                const std::vector<std::string> &getTeams() const { return this->_teams; }
                const std::vector<Egg> &getEggs() const { return this->_eggs; }
                const std::vector<Player> &getPlayers() const { return this->_players; }

                void updateTile(const size_t &x, const size_t &y, Tile &tile) { this->_map->setTile(x, y, tile); }

                void addTeam(const std::string &teamName) { this->_teams.push_back(teamName); }

                void addEgg(
                    const int &eggId,
                    const int &fatherId,
                    const int &x,
                    const int &y
                ) { this->_eggs.push_back(Egg(eggId, fatherId, x, y)); }
                void addPlayer(const Player &player) { this->_players.push_back(player); }

                void updatePlayerPosition(
                    const int &id,
                    const int &x,
                    const int &y,
                    const Orientation &orientation
                );
                void updatePlayerLevel(const int &id, const size_t &level);
                void updatePlayerInventory(const int &id, const Inventory &inventory);

                void PlayerExpulsion(const int &id);

                void PlayerBroadcast(const int &id, const std::string &message);

                void StartIncantation(
                    const int &x, const int &y,
                    const int &level,
                    const std::vector<int> &playerIds
                );
                void EndIncantation(const int &x, const int &y, const bool &result);

                void hatchEgg(const int &eggId);

                void removeEgg(const int &eggId);
                void removePlayer(const int &id);

                Egg &getEggById(const int &eggId);
                const Egg &getEggById(const int &eggId) const;

                Player &getPlayerById(const int &id);
                const Player &getPlayerById(const int &id) const;

                std::vector<Egg &> getEggsByCoord(const int &x, const int &y);
                const std::vector<const Egg> getEggsByCoord(const int &x, const int &y) const;

                std::vector<Player &> getPlayersByCoord(const int &x, const int &y);
                const std::vector<const Player> getPlayersByCoord(const int &x, const int &y) const;

                void endGame(const std::string &teamName);

            private:

                size_t _frequency;

                std::vector<Egg> _eggs;
                std::vector<Player> _players;
                std::vector<std::string> _teams;

                std::shared_ptr<game::Map> _map;
        };
    }
}
