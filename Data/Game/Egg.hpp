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
                int x;
                int y;

                explicit Egg(const int &id, const int &fatherId, const int &x, const int &y) :
                    x(x), y(y), _id(id), _fatherId(fatherId)
                {}
                explicit Egg(const int &id, const int &x, const int &y) :
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
