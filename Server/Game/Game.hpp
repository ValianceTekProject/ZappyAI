/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include <ctime>

#include "Data/Game/Map.hpp"

namespace zappy {
    namespace game {

        class MapServer : public Map
        {
            public:

                MapServer() = default;
                ~MapServer() = default;

                void MapInit();

            private:
                
        };

        class Game {
            
            public:
                Game() = default;
                ~Game() = default;

                MapServer &getMap() { return map; }
            
            private:
                MapServer map;

        };
        
        
    }
}