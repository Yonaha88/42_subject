NAME = codexion

CC = cc

CFLAGS = -Wall -Wextra -Werror -pthread

HEADER = codexion.h

SRCS =	codexion.c \
		parsing.c \
		init.c \
		cleanup.c \
		utils.c \
		clock.c \
		log.c \
		heap.c \
		heap_utils.c \
		scheduler.c \
		dongle_queue.c \
		dongle.c \
		dongle_utils.c \
		coder.c \
		monitor.c \

OBJS = $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $@

%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
