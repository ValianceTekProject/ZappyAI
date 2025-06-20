//
// EPITECH PROJECT, 2025
// Map
// File description:
// Map
//

#pragma once

#include "Egg.hpp"
#include "Map.hpp"
#include "Teams.hpp"
#include <queue>

namespace zappy {
    namespace game {

#define SERVER_FATHER_ID -1

        class MapServer : public Map {
           public:
            explicit MapServer(int mapWidth, int mapHeight);
            ~MapServer() = default;

            void setEggsonMap(std::vector<Team> &teamList, int clientNb);
            zappy::game::Egg popEgg();

           private:
            int _idEggTot = 0;
            void _placeResources();
            std::queue<Egg> _eggList;
        };

    }  // namespace game
}  // namespace zappy
