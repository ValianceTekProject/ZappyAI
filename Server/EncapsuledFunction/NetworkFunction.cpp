/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** NetworkFunction
*/

#include "Server.hpp"

int ZappyServer::my_socket(int __domain, int __type, int __protocol)
{
    return socket(__domain, __type, __protocol);
}

int ZappyServer::my_bind(int __fd, const sockaddr *__addr, socklen_t __len)
{
    return bind(__fd, __addr, __len);
}

int ZappyServer::my_listen(int __fd, int __n)
{
    return listen(__fd, __n);
}

int ZappyServer::my_poll(pollfd *__fds, nfds_t __nfds, int __timeout)
{
    return poll(__fds, __nfds, __timeout);
}

int ZappyServer::my_accept(int __fd, sockaddr *__restrict__ __addr, socklen_t *__restrict__ __addr_len)
{
    return accept(__fd, __addr, __addr_len);
}

sighandler_t ZappyServer::my_signal(int __sig, sighandler_t __handler)
{
    return signal(__sig, __handler);
}