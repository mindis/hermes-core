all:
	@gcc -g -I../../../../../include -L../../../../../build  \
	    hermes_client.c \
	    ../common/transport.c \
	    ../../utils/utils.c \
	    ../../utils/base64.c \
	    -std=c99 \
	    -lhermes_mid_hermes \
	    -lhermes_mid_hermes_ll \
	    -lhermes_credential_store \
	    -lhermes_data_store \
	    -lhermes_key_store \
	    -lhermes_rpc \
	    -lpthread \
	    -lhermes_common \
	    -lhermes_secure_transport \
	    -lthemis \
	    -lsoter \
	    -o client

clean:
	@rm ./client
