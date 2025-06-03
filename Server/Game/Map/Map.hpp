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
            MapServer() = default;
            ~MapServer() = default;

            void mapInit();

           private:
        };

    }  // namespace game
}  // namespace zappy
