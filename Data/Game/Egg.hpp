/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Egg.hpp
*/

#pragma once

#include <iostream>

namespace zappy {
    namespace game {
        class Egg
        {
            public:
                size_t x;
                size_t y;

                explicit Egg(int id, size_t x, size_t y) :
                    _id(id), _fatherId(-1), x(x), y(y)
                {}
                explicit Egg(int id, int fatherId, size_t x, size_t y) :
                    _id(id), _fatherId(fatherId), x(x), y(y)
                {}
                ~Egg() = default;

                const int getId() const { return this->_id; }

                int getFatherId() const { return this->_fatherId; }
                void setFatherId(int id) { this->_fatherId = id; }

            private:
                const int _id;
                int _fatherId;
        };
    }
}
