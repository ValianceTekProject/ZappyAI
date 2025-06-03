//
// EPITECH PROJECT, 2025
// Map
// File description:
// Map
//

#pragma once

#include "Data/Game/Map.hpp"

namespace zappy {
    namespace game {

        class MapServer : public Map {
           public:
            explicit MapServer(int mapWidth, int mapHeight);
            ~MapServer() = default;

           private:
            void _placeResources();
        };

    }  // namespace game
}  // namespace zappy
