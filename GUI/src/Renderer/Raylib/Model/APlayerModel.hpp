/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** APlayerModel.hpp
*/

#pragma once
#include "IPlayerModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class APlayerModel : public IPlayerModel {
                public:
                    virtual ~APlayerModel() = default;

                    virtual void init() override;

                    virtual void update() override;

                    virtual void walk() override;
                    virtual void ejected() override;
                    virtual void idle() override;

                    virtual void render() override;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
