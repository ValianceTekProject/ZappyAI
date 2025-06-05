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

                Egg(const int &id, const int &fatherId, const size_t &x, const size_t &y) :
                    x(x), y(y), _id(id), _fatherId(fatherId)
                {}
                Egg(const int &id, const size_t &x, const size_t &y) :
                    Egg(id, -1, x, y)
                {}
                ~Egg() = default;

                int getId() const { return this->_id; }

                int getFatherId() const { return this->_fatherId; }
                void setFatherId(const int &id) { this->_fatherId = id; }

            private:
                int _id;
                int _fatherId;
        };
    }
}
