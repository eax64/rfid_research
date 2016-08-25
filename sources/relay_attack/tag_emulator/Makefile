CC	= gcc
RM	= rm -f
CFLAGS	= -Wextra -Wall
LDFLAGS	= -lnfc

SRC1	= emulate.c
OBJ1	= $(SRC1:.c=.o)

SRC2	= getinfo.c
OBJ2	= $(SRC2:.c=.o)

NAME1	= emulate
NAME2	= getinfo

all: $(NAME1) $(NAME2)

$(NAME1): $(OBJ1)
	$(CC) $(LDFLAGS) -o $(NAME1) $(OBJ1)

$(NAME2): $(OBJ2)
	$(CC) $(LDFLAGS) -o $(NAME2) $(OBJ2)

clean:
	$(RM) $(OBJ1)
	$(RM) $(OBJ2)

fclean: clean
	$(RM) $(NAME1)
	$(RM) $(NAME2)

re: fclean all

.PHONY: all, clean, fclean, re
