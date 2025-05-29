/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.hpp
*/

#pragma once

#include "Map.hpp"

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

            private:
            size_t _frequency;

            game::Map _map;
        };
    }
}
