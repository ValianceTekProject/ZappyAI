/*
** EPITECH PROJECT, 2025
<<<<<<< HEAD
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
=======
** B-OOP-400-BDX-4-1-gui-baptiste.blambert
>>>>>>> 205ae46 (chore: architecture)
** File description:
** IError
*/

#pragma once

#include <iostream>
#include <stdexcept>

<<<<<<< HEAD
namespace zappy {
    namespace gui {
        class IError : public std::exception
        {
            public:
                virtual const char *what() const noexcept override = 0;
                virtual const char *where() const noexcept = 0;
        };
    }
=======
namespace gui {
    class IError : public std::exception
    {
        public:
            virtual const char *what() const noexcept override = 0;
            virtual const char *where() const noexcept = 0;
    };
>>>>>>> 205ae46 (chore: architecture)
}
