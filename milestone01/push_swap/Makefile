# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: hkanamit <hkanamit@student.42tokyo.jp>     +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/05/14 17:28:12 by hkanamit          #+#    #+#              #
#    Updated: 2026/05/19 16:03:55 by hkanamit         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME		= push_swap
BONUS_NAME	= checker

CC		= cc
CFLAGS		= -Wall -Wextra -Werror

SRCS		= atoi.c bench_mark.c buble_sort.c call_algo.c chunk_based_sort.c \
		  disorder.c ft_printf.c ft_printf2.c ft_printf3.c helper_func.c \
		  judge.c list.c lsd_sort.c main.c push.c rank.c \
		  reverse_rotate.c rotate.c swap.c small_sort.c

BONUS_SRCS	= checker_bonus.c checker_push_bonus.c checker_swap_bonus.c \
		  checker_rotate_bonus.c checker_revrotate_bonus.c \
		  checker_readline_bonus.c atoi.c helper_func.c list.c

OBJS		= $(SRCS:.c=.o)
BONUS_OBJS	= $(BONUS_SRCS:.c=.o)

all:		$(NAME)

$(NAME):	$(OBJS)
		$(CC) $(CFLAGS) -o $(NAME) $(OBJS)

bonus:		$(BONUS_OBJS)
		$(CC) $(CFLAGS) -o $(BONUS_NAME) $(BONUS_OBJS)

%.o:		%.c
		$(CC) $(CFLAGS) -I . -c $< -o $@

clean:
		rm -f $(OBJS) $(BONUS_OBJS)

fclean:		clean
		rm -f $(NAME) $(BONUS_NAME)

re:		fclean all

.PHONY:		all bonus clean fclean re
