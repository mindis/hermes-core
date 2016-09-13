/*
 * Copyright (c) 2016 Cossack Labs Limited
 */

#ifndef MIDHERMES_HERMES_H_
#define MIDHERMES_HERMES_H_

#include "config.h"

typedef struct hermes_client_t_ hermes_client_t;

hermes_client_t* hermes_client_create(const config_t* config);
void hermes_client_destroy(hermes_client_t** ctx);

//credential store
int hermes_client_get_public_key(hermes_client_t* ctx, const char* user_id, uint8_t** res, size_t* res_length);

//record_set
int hermes_client_get_docs_list(hermes_client_t* ctx, char** res);
int hermes_client_get_users_list(hermes_client_t* ctx, const char* user_id, char** res);
int hermes_client_read_doc(hermes_client_t* ctx, const char* user_id, const char* id, char** res);
int hermes_client_add_doc(hermes_client_t* ctx, const char* user_id, const char* doc, const uint8_t* mac, const size_t mac_length, const uint8_t* rt, const size_t rt_length, const uint8_t* ut, const size_t ut_length, const uint8_t* pub_key, const size_t pub_key_length);
int hermes_client_update_doc(hermes_client_t* ctx, const char* user_id, const char* doc, const uint8_t* mac, const size_t mac_length, const char* doc_id, const uint8_t* old_mac, const size_t ild_mac_length);
int hermes_client_add_public_block(hermes_client_t* ctx, const char* user_id, const char* doc_id, const uint8_t* mac, const size_t mac_length, const char* name, const uint8_t* block, const size_t block_length);
int hermes_client_add_private_block(hermes_client_t* ctx, const char* user_id, const char* doc_id, const uint8_t* mac, const size_t mac_length, const char* name, const uint8_t* block, const size_t block_length);
int hermes_client_add_access(hermes_client_t* ctx, const char* user_id, const char* doc_id, const uint8_t* mac, const size_t mac_length, const char* new_user_name, const uint8_t* ut, const size_t ut_length, const uint8_t* rt, const size_t rt_length, const uint8_t* pubk, const size_t pubk_length);
int hermes_client_rm_access(hermes_client_t* ctx, const char* user_id, const char* doc_id, const uint8_t* mac, const size_t mac_length, const char* new_user_name);
int hermes_client_get_public_block(hermes_client_t* ctx, const char* user_id, const char* block_id, const char* doc_id, uint8_t** block, size_t* block_length);
int hermes_client_get_private_block(hermes_client_t* ctx, const char* user_id, const char* block_id, const char* doc_id, uint8_t** block, size_t* block_length);
int hermes_client_rm_public_block(hermes_client_t* ctx, const char* user_id, const char* block_id, const char* doc_id, const uint8_t* mac, const size_t mac_length);
int hermes_client_rm_private_block(hermes_client_t* ctx, const char* user_id, const char* block_id, const char* doc_id, const uint8_t* mac, const size_t mac_length);

#endif /* MIDHERMES_HERMES_H_ */