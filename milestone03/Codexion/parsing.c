/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parsing.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:06 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:39:49 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static int	is_valid_number(char *str)
{
	int	i;
	int	num_only;

	num_only = 1;
	i = 0;
	if (str[0] == '\0')
		return (0);
	while (str[i] != '\0')
	{
		if (!('0' <= str[i] && str[i] <= '9'))
		{
			num_only = 0;
			break ;
		}
		i++;
	}
	return (num_only);
}

static int	arg_error(char *name, char *why)
{
	fprintf(stderr, "Error: %s: %s\n", name, why);
	return (0);
}

static int	parse_num(char *str, long *out, char *name, long min)
{
	int		i;
	long	value;

	if (!is_valid_number(str))
		return (arg_error(name, "must be a non-negative integer"));
	i = 0;
	value = 0;
	while (str[i] != '\0')
	{
		if (value > (INT_MAX - (str[i] - '0')) / 10)
			return (arg_error(name, "out of range (max 2147483647)"));
		value = value * 10 + (str[i] - '0');
		i++;
	}
	if (value < min)
		return (arg_error(name, "must be 1 or greater"));
	*out = value;
	return (1);
}

static int	parse_scheduler(char *str, t_scheduler *out)
{
	if (strcmp(str, "fifo") == 0)
	{
		*out = CODEX_FIFO;
		return (1);
	}
	if (strcmp(str, "edf") == 0)
	{
		*out = CODEX_EDF;
		return (1);
	}
	return (arg_error("scheduler", "must be \"fifo\" or \"edf\""));
}

int	parse_args(int argc, char **argv, t_args *args)
{
	long	tmp;

	if (argc != 9)
		return (arg_error("arguments", "expected exactly 8"));
	if (!parse_num(argv[1], &tmp, "number_of_coders", 1))
		return (0);
	args->number_of_coders = (int)tmp;
	if (!parse_num(argv[2], &args->time_to_burnout, "time_to_burnout", 0))
		return (0);
	if (!parse_num(argv[3], &args->time_to_compile, "time_to_compile", 0))
		return (0);
	if (!parse_num(argv[4], &args->time_to_debug, "time_to_debug", 0))
		return (0);
	if (!parse_num(argv[5], &args->time_to_refactor, "time_to_refactor", 0))
		return (0);
	if (!parse_num(argv[6], &tmp, "number_of_compiles_required", 0))
		return (0);
	args->number_of_compiles_required = (int)tmp;
	if (!parse_num(argv[7], &args->dongle_cooldown, "dongle_cooldown", 0))
		return (0);
	if (!parse_scheduler(argv[8], &args->scheduler))
		return (0);
	return (1);
}
