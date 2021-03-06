/*
* Copyright (c) 2017 Cossack Labs Limited
*
* This file is a part of Hermes-core.
*
* Hermes-core is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Hermes-core is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.
*
* You should have received a copy of the GNU Affero General Public License
* along with Hermes-core.  If not, see <http://www.gnu.org/licenses/>.
*
*/



#include "transport.h"

#include <hermes/common/errors.h>
#include <assert.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>

hm_rpc_transport_t *server_connect(const char *ip, int port) {
    int64_t sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        fprintf(stderr, "connection error (1) (%s:%i)\n", ip, port);
        return NULL;
    }
    struct sockaddr_in server;
    server.sin_addr.s_addr = inet_addr(ip);
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    if (connect(sock, (struct sockaddr *) &server, sizeof(server)) < 0) {
        fprintf(stderr, "connection error (2) (%s:%i)\n", ip, port);
        return NULL;
    }

    hm_rpc_transport_t *transport = transport_create(sock);
    if (!transport) {
        close(sock);
        fprintf(stderr, "connection error (3) (%s:%i)\n", ip, port);
        return NULL;
    }
    return transport;
}

typedef struct transport_type {
    int socket;
} transport_t;

uint32_t transport_send(void *t, const uint8_t *buf, const size_t buf_length) {
    transport_t* transport = (transport_t *) t;
    if (!t || !buf || !buf_length) {
        return HM_FAIL;
    }
    ssize_t written = write(transport->socket, buf, buf_length);
    if (written < 0 || buf_length != (size_t)written) {
        return HM_FAIL;
    }
    return HM_SUCCESS;
}

uint32_t transport_recv(void *t, uint8_t *buf, size_t buf_length) {
    if (!t || !buf || !buf_length) {
        return HM_FAIL;
    }
    ssize_t readed_bytes = 0;
    size_t total_read = 0;
    while (total_read < buf_length) {
        readed_bytes = read(((transport_t *) t)->socket, buf + total_read, buf_length - total_read);
        if (readed_bytes < 0) {
            return HM_FAIL;
        }
        total_read += readed_bytes;
        if(readed_bytes == 0 || (size_t)readed_bytes < buf_length){
            break;
        }
    }
    return HM_SUCCESS;
}

hm_rpc_transport_t *transport_create(int socket) {
    if (socket < 0) {
        return NULL;
    }
    hm_rpc_transport_t *res = calloc(1, sizeof(hm_rpc_transport_t));
    assert(res);
    res->user_data = calloc(1, sizeof(transport_t));
    assert(res->user_data);
    ((transport_t *) (res->user_data))->socket = socket;
    res->send = transport_send;
    res->recv = transport_recv;
    return res;
}

uint32_t transport_destroy(hm_rpc_transport_t **t) {
    if (!t || !(*t) || !((*t)->user_data)) {
        return HM_FAIL;
    }
    close(((transport_t *) ((*t)->user_data))->socket);
    free((*t)->user_data);
    free(*t);
    *t = NULL;
    return HM_SUCCESS;
}
