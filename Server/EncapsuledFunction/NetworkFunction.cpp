/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** NetworkFunction
*/

#include "Server.hpp"
#include <exception>
//
// int zappy::my_socket(int __domain, int __type, int __protocol)
// {
//     return socket(__domain, __type, __protocol);
// }
//
// int zappy::my_bind(int __fd, const sockaddr *__addr, socklen_t __len)
// {
//     return bind(__fd, __addr, __len);
// }
//
// int zappy::my_listen(int __fd, int __n)
// {
//     return listen(__fd, __n);
// }
//
// int zappy::my_poll(pollfd *__fds, nfds_t __nfds, int __timeout)
// {
//     return poll(__fds, __nfds, __timeout);
// }
//
// int zappy::my_accept(int __fd, sockaddr *__restrict__ __addr, socklen_t *__restrict__ __addr_len)
// {
//     return accept(__fd, __addr, __addr_len);
// }

void zappy::my_signal(int __sig, sighandler_t __handler)
{
    if (signal(__sig, __handler) == SIG_ERR)
        throw zappy::error::Error("Unable to use signal");
}
