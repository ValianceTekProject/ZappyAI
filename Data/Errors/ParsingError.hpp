/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** ParsingError
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    class ParsingError : public AError
    {
        public:
            ParsingError(const std::string &msg, const std::string &where)
                noexcept : AError(msg, where) {};
    };
}
