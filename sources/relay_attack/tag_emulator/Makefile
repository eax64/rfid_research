CC	= gcc
RM	= rm -f
CFLAGS	= -Wextra -Wall
LDFLAGS	= -lnfc

SRC	= emulate.c
OBJ	= $(SRC:.c=.o)

NAME	= emulate

all: $(NAME)

$(NAME): $(OBJ)
	$(CC) $(LDFLAGS) -o $(NAME) $(OBJ)

clean:
	$(RM) $(OBJ)

fclean: clean
	$(RM) $(NAME)

re: fclean all

.PHONY: all, clean, fclean, re
