/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   helper_func.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/15 10:57:04 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:43:43 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	strcmp_original(char *s1, char *s2)
{
	int	idx;

	idx = 0;
	while (s2[idx] && s1[idx] == s2[idx])
		idx++;
	if (s1[idx] == s2[idx])
		return (1);
	return (0);
}

static int	ft_isdigit(int c)
{
	if ('0' <= c && c <= '9')
		return (1);
	return (0);
}

static int	validate_arg(char *arg)
{
	int	j;

	j = 0;
	if (arg[j] == '-' || arg[j] == '+')
		j++;
	if (arg[j] == '\0')
		return (0);
	if (arg[j] == '0' && arg[j + 1] != '\0')
		return (0);
	while (arg[j])
	{
		if (ft_isdigit(arg[j]) == 0)
			return (0);
		j++;
	}
	return (1);
}

int	error_handle(int argc, char *argv[])
{
	int	i;

	i = 0;
	while (++i < argc)
	{
		if (validate_arg(argv[i]) == 0)
		{
			write(2, "Error\n", 6);
			return (0);
		}
	}
	return (1);
}

int	detect_duplicate_values(t_list *lst, int a)
{
	t_list	*tmp;

	tmp = lst;
	while (tmp != NULL)
	{
		if (tmp->content == a)
			return (-1);
		tmp = tmp->next;
	}
	return (1);
}
