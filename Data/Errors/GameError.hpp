/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** GameError
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    namespace game {
        class GameError : public AError
        {
            public:
                GameError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
}
