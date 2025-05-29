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

                void setFrequency(size_t frequency) { _frequency = frequency; }
                void initMap(size_t width, size_t height) { _map.init(width, height); }

                size_t getFrequency() const { return _frequency; }

                void updateTile(size_t x, size_t y, Tile tile) { _map.setTile(x, y, tile); }

                void addTeam(const std::string &teamName) { _teams.push_back(teamName); }

                void addPlayer(Player player) { _players.push_back(player); }
                void updatePlayerPosition(size_t id,
                    size_t x,
                    size_t y,
                    Orientation orientation
                );
                void updatePlayerLevel(size_t id,
                    size_t level
                );
                void updatePlayerInventory(size_t id,
                    Inventory &inventory
                );
                void removePlayer(size_t id);

                void endGame(const std::string &teamName);

            private:
            size_t _frequency;

            std::vector<Player> _players;
            std::vector<std::string> _teams;

            game::Map _map;
        };
    }
}
